from django.db.models import Q
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from usercenter.permissions import IsSuperuserOrReadOnly, IsSuperuser
from usercenter.serializers import FuncPermissionSerializer

from . import filters
from . import models
from . import serializers


class SystemViewSet(ModelViewSet):
    """系统"""
    queryset = models.System.objects.order_by('sys_id')
    serializer_class = serializers.SystemSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = filters.SystemFilterSet
    search_fields = ('name',)


class SystemOrgViewSet(ModelViewSet):
    """系统租户"""
    queryset = models.SystemOrg.objects.order_by('pk')
    serializer_class = serializers.SystemOrgSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ('name',)
    filterset_fields = (
        'sys_id', 'org_id', 'system', 'name', 'manager'
    )


class SystemOrgPermissionsViewSet(ReadOnlyModelViewSet):
    """系统租户功能权限"""
    queryset = models.SystemOrg.objects.order_by('pk')
    serializer_class = FuncPermissionSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        sys_id = request.GET.get('sys_id')
        org_id = request.GET.get('org_id')
        if not sys_id or not org_id:
            return Response([])
        sys_org = models.SystemOrg.objects.filter(sys_id=sys_id, org_id=org_id).first()
        if not sys_org:
            return Response([])
        perms = sys_org.permissions.all()
        return Response(self.get_serializer(perms, many=True).data)


class SystemBizViewSet(ModelViewSet):
    """业务子系统定义"""
    queryset = models.SystemBiz.objects.order_by('pk')
    serializer_class = serializers.SystemBizSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_fields = (
        'sys_id', 'biz_id', 'system', 'name',
    )


class SMSConfigViewSet(ModelViewSet):
    """短信平台配置"""
    queryset = models.SMSConfig.objects.order_by('pk')
    serializer_class = serializers.SMSConfigSerializer
    permission_classes = [IsSuperuser]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = filters.SMSConfigFilterSet
    search_fields = ('name',)


class EmailConfigViewSet(ModelViewSet):
    """邮件平台配置"""
    queryset = models.EmailConfig.objects.order_by('pk')
    serializer_class = serializers.EmailConfigSerializer
    permission_classes = [IsSuperuser]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_fields = ('system', 'system_org', 'name')
    search_fields = ('name',)


class WechatConfigViewSet(ModelViewSet):
    """系统微信相关配置"""
    queryset = models.WechatConfig.objects.order_by('pk')
    serializer_class = serializers.WechatConfigSerializer
    permission_classes = [IsSuperuser]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.WechatConfigFilterSet


class SystemProjectViewSet(ModelViewSet):
    """系统项目工程配置"""
    queryset = models.SystemProject.objects.order_by('system', 'name')
    serializer_class = serializers.SystemProjectSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = filters.SystemProjectFilterSet
    search_fields = ('name',)


class SystemProjectRouterViewSet(ReadOnlyModelViewSet):
    """系统项目工程源码路由配置读取"""
    queryset = models.SystemProject.objects.order_by('system', 'name')
    serializer_class = serializers.SystemProjectRouterSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = filters.SystemProjectFilterSet
    search_fields = ('name',)


class SystemPRViewSet(ModelViewSet):
    """系统项目工程路由配置"""
    queryset = models.SystemProjectRouter.objects.order_by('sys_id', 'project', 'tree_id')
    serializer_class = serializers.SystemPRSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SystemProjectRouterFilterSet


class SystemPRMoveView(GenericViewSet):
    """分类树排列移动"""
    queryset = models.SystemProjectRouter.objects.none()
    serializer_class = serializers.SystemPRMoveSerializer
    permission_classes = [IsSuperuserOrReadOnly]

    def create(self, request, *args, **kwargs):
        """response: {'error': false, 'msg': '修改成功'}"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': serializer.errors})


class SystemPMViewSet(ModelViewSet):
    """系统项目工程菜单配置"""
    queryset = models.SystemProjectMenu.objects.order_by('sys_id', 'project', 'tree_id')
    serializer_class = serializers.SystemPMSerializer
    permission_classes = [IsSuperuserOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SystemProjectMenuFilterSet

    def list(self, request, *args, **kwargs):
        project = request.GET.get('project')
        if not project:
            return Response([])
        return super().list(request, *args, **kwargs)


class MySystemPMViewSet(ReadOnlyModelViewSet):
    """当前用户的系统项目工程菜单"""
    queryset = models.SystemProjectMenu.objects.order_by('sys_id', 'project', 'tree_id')
    serializer_class = serializers.MySystemPMSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SystemProjectMenuFilterSet

    def get_queryset(self):
        perms = self.perms_cache
        return super().get_queryset().filter(
            Q(level=0) & (Q(permission__in=perms) | Q(permission__isnull=True))
        )

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @property
    def perms_cache(self):
        if hasattr(self, '_perms'):
            return self._perms
        user = self.request.user
        if user.is_anonymous:
            self._perms = []
        else:
            self._perms = list(tuple(user.get_permissions().values_list('pk', flat=True)))
        return self._perms


class SystemPMMoveView(GenericViewSet):
    """系统项目工程菜单排列移动"""
    queryset = models.SystemProjectMenu.objects.none()
    serializer_class = serializers.SystemPMMoveSerializer
    permission_classes = [IsSuperuserOrReadOnly]

    def create(self, request, *args, **kwargs):
        """response: {'error': false, 'msg': '修改成功'}"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': serializer.errors})


class SystemLogViewSet(ModelViewSet):
    """系统日志"""
    queryset = models.SystemLog.objects.order_by('-create_time')
    serializer_class = serializers.SystemLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SystemLogFilterSet


class SystemDataBackupViewSet(ModelViewSet):
    """系统备份"""
    queryset = models.SystemDataBackup.objects.order_by('-create_time')
    serializer_class = serializers.SystemDataBackupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('sys_id', 'org_id', 'user_name')
