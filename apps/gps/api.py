from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.utils.json import dumps, loads
from django_redis import get_redis_connection
from . import serializers
from . import models
from . import filters


cache = get_redis_connection("default")


class LastPointViewSet(CreateModelMixin, GenericViewSet):
    queryset = models.Point.objects.order_by('-create_time')
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.LastPointSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_class = filters.LastPointFilterSet

    def create(self, request, *args, **kwargs):
        """最后定位信息API

        根据 sn（可多个）返回每个sn对应最后定位信息的数组，`返回值结构`：

        ```
        {
          "sn-001": {
            "pk": "123-123-123...",
            "sys_id": 1,
            "org_id": 1,
            "sn": "sn-001",
            "longitude": 123.123124,
            "latitude": 123.123123,
            ... 同 gps-point API 数据结构
          }
        }
        ```
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        sys_id = data['sys_id']
        org_id = data['org_id']
        sn_list = data['sn']
        points = {}
        for i in sn_list:
            if not i:
                continue
            val = cache.get(f'gps-point-{i}')
            val = loads(val) if val else None
            if val and isinstance(val, dict) and \
               val.get('sys_id') == sys_id and \
               val.get('org_id') == org_id:
                points[i] = val
            elif val is None:
                val = models.Point.objects.filter(sn=i).order_by('-create_time').first()
                if val:
                    points[i] = serializers.PointSerializer(instance=val).data
            else:
                points[i] = val
        return Response(points)


class RefreshLastPointViewSet(CreateModelMixin, GenericViewSet):
    queryset = models.Point.objects.order_by('-create_time')
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.RefreshLastPointSerializer
    filter_backends = (DjangoFilterBackend,)

    def create(self, request, *args, **kwargs):
        """更新最后定位信息API

        根据 sn（可多个）更新每个sn对应最后定位信息的数组，`无返回值！`
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        sys_id = data['sys_id']
        org_id = data['org_id']
        sn_list = data['sn']
        sql = """
            with T as (
              select
                *,
                row_number() over (
                  partition by fd.sn
                  order by
                    fd.create_time desc
                ) as rownum
              from
                gps_point as fd
              where
                fd.org_id = %s and 
                fd.sys_id = %s and
                fd.sn in %s
            )
            select * from T where rownum = 1
        """
        qs = models.Point.objects.raw(sql, (org_id, sys_id, tuple(sn_list),))
        cache = get_redis_connection("default")
        for i in qs:
            cache.set(f'gps-point-{i.sn}', dumps(serializers.PointSerializer(instance=i).data))
        return Response('success')


class PointViewSet(ModelViewSet):
    """地图标记记录API gps_point geo_type='point'"""
    queryset = models.Point.objects.order_by('-create_time')
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.PointSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.PointFilterSet

    def perform_create(self, serializer: serializers.PointSerializer):
        instance = serializer.save()
        data = serializer.data
        cache.set(f'gps-point-{instance.sn}', dumps(data))

    def perform_update(self, serializer):
        instance = serializer.save()
        data = serializer.data
        cache.set(f'gps-point-{instance.sn}', dumps(data))


class PointFindViewSet(PointViewSet):
    """地图标记查询API"""
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        self.request._request.GET = self.request.data.copy()
        return super().list(request, *args, **kwargs)


class PointTimeViewSet(ListModelMixin, GenericViewSet):
    """地图标记时间API"""
    queryset = models.Point.objects.order_by('-client_time')
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.PointSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.PointTimeFilterSet

    def list(self, request, *args, **kwargs):
        """
        根据时间点和sn号返回指定时间点之前的最近一条定位信息

        必传参数：
        - sn: 设备号
        - time_point: 时间点
        - sys_id: 系统ID
        - org_id: 组织ID
        """
        required_args = ['sn', 'time_point', 'sys_id', 'org_id']
        for req_f in required_args:
            if req_f not in request.GET:
                return Response(f'缺少参数 {req_f}', status=400)
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.order_by('-client_time').last()
        if not obj:
            return Response({}, status=404)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class PolygonViewSet(ModelViewSet):
    """地图多边形API gps_polygon"""
    queryset = models.Polygon.objects.order_by('-create_time')
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = serializers.PolygonSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.PolygonFilterSet
