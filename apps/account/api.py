from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from django_filters.rest_framework.backends import DjangoFilterBackend
from utility.filter_backends import SearchBackend
from . import serializers
from . import models
from . import filters


class AccountViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.Account.objects.order_by('pk')
    serializer_class = serializers.AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchBackend,)
    filterset_class = filters.AccountFilterSet
    search_fields = (
        'acc_1_name',
        'acc_2_name',
        'acc_3_name',
        'acc_1_type',
        'acc_2_type',
        'acc_3_type',
        'jifen_acc',
    )

    def list(self, request, *args, **kwargs):
        """
        账户查询

        根据查询条件返回
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        账户详情

        根据ID返回对应的账户详情
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        账户修改

        仅可修改账户名称信息
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        账户局部修改

        仅可修改账户名称信息
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        账户删除

        只有管理员用户和账户关联的用户本人才能删除
        """
        instance = self.get_object()  # type: models.Account
        user = request.user
        if user.is_superuser or user == instance.user:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response('delete not allowed!', status=403)


class MyAccountView(viewsets.GenericViewSet):
    queryset = models.Account.objects.order_by('pk')
    serializer_class = serializers.AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        我的账户

        根据当前登录用户返回用户拥有的首个账户，未查询到时返回 status 404
        """
        user = request.user
        acc = models.Account.objects.filter(user=user).order_by('-create_time').first()
        if acc is None:
            return Response('Account not found!', status=404)
        serializer = self.get_serializer(acc)
        return Response(serializer.data)


class AccountCreateView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Account.objects.order_by('pk')
    serializer_class = serializers.AccountCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        账户创建

        余额和锁定均为0，无需传入
        """
        return super().create(request, *args, **kwargs)


class AccountStatementsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AccountStatements.objects.order_by('pk')
    serializer_class = serializers.AccountStatementsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchBackend,)
    filterset_class = filters.AccountStatementsFilterSet
    search_fields = (
        'acc__acc_1_name',
        'acc__acc_2_name',
        'acc__acc_3_name',
        'acc__acc_1_type',
        'acc__acc_2_type',
        'acc__acc_3_type',
    )

    def list(self, request, *args, **kwargs):
        """
        账户明细查询

        根据传入条件查询账户流水
        """
        return super().list(request, *args, **kwargs)
