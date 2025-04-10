from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from . import models
from . import serializers
from . import filters


class FlatBaseTreeViewSet(viewsets.ModelViewSet):
    """分类树平铺API baseconfig_basetree"""

    queryset = models.BaseTree.objects.all()
    serializer_class = serializers.FlatBaseTreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.FlatBaseTreeFilterSet


class BaseTreeViewSet(viewsets.ModelViewSet):
    """分类树树形API(从根节点开始) baseconfig_basetree"""

    queryset = models.BaseTree.objects.all()
    serializer_class = serializers.BaseTreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.BaseTreeFilterSet

    def list(self, request, *args, **kwargs):
        if request.query_params.get('use_cache'):
            data = self.get_from_cache()
            if data:
                return Response(data)
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(qs, many=True)
        if request.query_params.get('use_cache'):
            cache_key = self.request.get_full_path()
            cache.set(cache_key, serializer.data, 1 * 60 * 60)
        return Response(serializer.data)

    def get_from_cache(self):
        cache_key = self.request.get_full_path()
        return cache.get(cache_key)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_org_id = instance.org_id
        old_biz_id = instance.biz_id
        new_instance = serializer.save()  # type: models.BaseTree
        new_org_id = new_instance.org_id
        new_biz_id = new_instance.biz_id
        if new_org_id != old_org_id:
            new_instance.get_family().update(org_id=new_org_id)
        if new_biz_id != old_biz_id:
            new_instance.get_family().update(biz_id=new_biz_id)


class BaseTreeMoveView(viewsets.GenericViewSet):
    """分类树排列移动"""
    queryset = models.BaseTree.objects.none()
    serializer_class = serializers.BaseTreeMoveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """response: {'error': false, 'msg': '修改成功'}"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': serializer.errors})


class BaseTreeCopyView(viewsets.GenericViewSet):
    """分类树复制API"""

    queryset = models.BaseTree.objects.none()
    serializer_class = serializers.BaseTreeCopySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        s2 = serializers.BaseTreeSerializer(instance=instance)
        return Response(s2.data)


class BaseConfigFileUploadViewSet(viewsets.ModelViewSet):
    """基础配置项文件API baseconfig_baseconfigfileupload"""

    queryset = models.BaseConfigFileUpload.objects.filter(is_deleted=False)
    serializer_class = serializers.BaseConfigFileUploadSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = filters.BaseConfigFileUploadFilterSet
    search_fields = ('file', 'file_name',)

    def perform_destroy(self, instance: models.BaseConfigFileUpload):
        instance.file.delete(save=False)
        super().perform_destroy(instance)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_anonymous:
            user = None
        instance = serializer.save()
        instance.user=user
        instance.save()


class BaseConfigFileFindViewSet(viewsets.ReadOnlyModelViewSet):
    """基础配置项文件API baseconfig_baseconfigfileupload"""

    queryset = models.BaseConfigFileUpload.objects.filter(is_deleted=False)
    serializer_class = serializers.BaseConfigFileUploadSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = filters.BaseConfigFileUploadFilterSet
    search_fields = ('file', 'file_name',)

    def create(self, request, *args, **kwargs):
        self.request._request.GET = self.request.data.copy()
        request = self.request
        return self.list(request, *args, **kwargs)
