from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import UserFilterSet, DepartmentFilterSet, FuncPermissionTreeFilterSet
from .permissions import CsrfExemptSessionAuthentication, BasicAuthentication
from . import models
from . import serializers


class ChangePasswordApi(viewsets.GenericViewSet):
    """
    修改密码
    """
    queryset = models.User.objects.none()
    serializer_class = serializers.ChangePwdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        修改当前用户密码
        """
        serializer = self.get_serializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': '原密码不正确'})


class UserViewSet(viewsets.ModelViewSet):
    """用户API usercenter_user"""

    queryset = models.User.objects.exclude(username='AnonymousUser')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilterSet
    search_fields = ['username', 'full_name', 'mobile']

    def perform_create(self, serializer):
        super().perform_create(serializer)
        if self.request.data.get('password'):
            serializer.instance.set_password(self.request.data.get('password'))
            serializer.instance.password_date = timezone.now()
            serializer.instance.save()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        if self.request.data.get('password'):
            serializer.instance.set_password(self.request.data.get('password'))
            serializer.instance.password_date = timezone.now()
            serializer.instance.save()

    def destroy(self, request, *args, **kwargs):
        """
        禁用或删除用户

        直接请求为禁用用户，带上query参数 "real=true" 即可真删除用户
        """
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        real = self.request.GET.get('real')
        if real:
            instance.delete()
            return
        instance.is_active = False
        instance.save()


class UserFindAPI(viewsets.GenericViewSet):
    """用户搜索"""
    queryset = models.User.objects.none()
    serializer_class = serializers.UserFindSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """根据search字段填写的用户姓名或手机号查找用户，找到唯一用户时返回用户信息（pk、full_name等）字段，未找到或找到多个时只返回数量"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class UserMinViewSet(viewsets.ReadOnlyModelViewSet):
    """用户API usercenter_user"""

    queryset = models.User.objects.exclude(username='AnonymousUser').select_related('department')
    serializer_class = serializers.UserMinSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilterSet
    search_fields = ['username', 'full_name', 'mobile']


class PermissionViewSet(viewsets.ModelViewSet):
    """权限API usercenter_funcpermission"""
    queryset = models.FuncPermission.objects.all()
    serializer_class = serializers.FuncPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('sys_id', 'org_id', 'biz_id',)

    def perform_destroy(self, instance):
        from rest_framework import status
        if self.request.GET.get('real'):
            instance.delete()

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.creator is None:
            instance.creator = self.request.user
            instance.save()
        return instance


class PermissionTreeViewSet(viewsets.ReadOnlyModelViewSet):
    """权限树API usercenter_funcpermission"""
    queryset = models.FuncPermission.objects.all()
    serializer_class = serializers.FuncPermissionTreeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FuncPermissionTreeFilterSet


class GroupViewSet(viewsets.ModelViewSet):
    """权限组API usercenter_funcgroup"""
    queryset = models.FuncGroup.objects.order_by('sort_num', 'pk')
    serializer_class = serializers.FuncGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('sys_id', 'org_id', 'biz_id',)


class DepartmentViewSet(viewsets.ModelViewSet):
    """机构部门API usercenter_department"""

    queryset = models.Department.objects.all()
    serializer_class = serializers.FlatDepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = DepartmentFilterSet
    search_fields = ('name', )


class TreeDepartmentViewSet(viewsets.ModelViewSet):
    """树形机构部门API usercenter_department"""

    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = DepartmentFilterSet
    search_fields = ('name',)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(models.Department.objects.root_nodes())
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)


class TxlViewSet(viewsets.ReadOnlyModelViewSet):
    """树形部门通讯录 API usercenter_department"""
    queryset = models.Department.objects.all()
    serializer_class = serializers.TxlSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('sys_id', 'org_id',)

    def list(self, request, *args, **kwargs):
        if 'sys_id' not in request.GET:
            return Response([])
        qs = self.filter_queryset(models.Department.objects.root_nodes())
        qs = models.Department.objects.filter(parent__in=qs).order_by('lft')
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)


class MyInfoViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    """我的信息API usercenter_user"""
    queryset = models.User.objects.none()
    serializer_class = serializers.MyinfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)


class DepartmentMoveView(viewsets.GenericViewSet):
    """部门排列移动"""
    queryset = models.Department.objects.none()
    serializer_class = serializers.DepartmentMoveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': False, 'msg': '修改成功'})
        else:
            return Response({'error': True, 'msg': serializer.errors})


class UserPhoneRegView(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """用户手机号注册API"""
    queryset = models.User.objects.none()
    serializer_class = serializers.UserPhoneRegSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny, )

    def create(self, request, *args, **kwargs):
        """需要先POST请求/api/v1/captcha/接口获取验证码key和图片"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        if instance.phone and not instance.mobile:
            instance.mobile = instance.phone
            instance.phone = None
        if self.request.data.get('password'):
            instance.set_password(self.request.data.get('password'))
            instance.password_date = timezone.now()
        else:
            instance.set_password(models.User.objects.make_random_password())
        instance.save()


class UserPhoneCheck(viewsets.GenericViewSet):
    queryset = models.User.objects.none()
    serializer_class = serializers.UserPhoneCheckSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        sys_id = serializer.validated_data['sys_id']
        qs = models.User.objects.filter(mobile=phone, sys_id=sys_id)
        if qs:
            data = {'phone': phone, 'sys_id': sys_id, 'exist': True}
        else:
            data = {'phone': phone, 'sys_id': sys_id, 'exist': False}
        return Response(data, status=200)


class UserCaptchaRegView(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """用户图片验证码注册API"""
    queryset = models.User.objects.none()
    serializer_class = serializers.UserCaptchaRegSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny, )

    def create(self, request, *args, **kwargs):
        """需要先POST请求/api/v1/captcha/接口获取验证码key和图片"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        if self.request.data.get('password'):
            instance.set_password(self.request.data.get('password'))
            instance.password_date = timezone.now()
        else:
            instance.set_password(models.User.objects.make_random_password())
        instance.save()


class OrgUserCaptchaRegView(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """用户图片验证码注册API"""
    queryset = models.User.objects.none()
    serializer_class = serializers.OrgUserCaptchaRegSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication,)
    permission_classes = (AllowAny, )

    def create(self, request, *args, **kwargs):
        """需要先POST请求/api/v1/captcha/接口获取验证码key和图片"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        if self.request.data.get('password'):
            instance.set_password(self.request.data.get('password'))
            instance.password_date = timezone.now()
        else:
            instance.set_password(models.User.objects.make_random_password())
        instance.save()
