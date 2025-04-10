from rest_framework import viewsets, permissions
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Q

from . import models
from . import serializers
from . import filters


class NoticeViewSet(viewsets.ModelViewSet):
    """通知公告API notice_notice"""

    queryset = models.MailBox.objects.filter(category='notice')
    serializer_class = serializers.NoticeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = filters.NoticeFilterSet
    search_fields = ('title',)


class ViewMyNoticeViewSet(viewsets.ReadOnlyModelViewSet):
    """登录用户查看通知公告API notice_notice"""

    queryset = models.MailBox.objects.filter(category='notice')
    serializer_class = serializers.NoticeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.NoticeFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_anonymous:
            return qs.none()
        user = self.request.user
        dep = user.department
        deps = []
        if dep:
            deps = dep.get_ancestors(include_self=True).values_list('pk', flat=True)
        if deps:
            return qs.filter(
                Q(is_public=True) | Q(public_user=self.request.user) | (
                    Q(departments__in=deps) & Q(department_range='本级及以下')
                )
            )
        else:
            return qs.filter(
                Q(is_public=True) | Q(public_user=self.request.user) | (
                    Q(departments=self.request.user.department) & Q(department_range='本级')
                )
            )


class MailBoxViewSet(viewsets.ModelViewSet):
    """用户系统消息API notice_mailbox"""
    queryset = models.MailBox.objects.filter(category='mailbox')
    serializer_class = serializers.MailBoxSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.MailBoxFilter


class MailBoxBulkCreateViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    """用户系统消息API notice_mailbox"""
    queryset = models.MailBox.objects.filter(category='mailbox')
    serializer_class = serializers.MailBoxBulkCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True}, status=201)


class MailBoxUnreadCountView(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    """用户未读系统消息数API notice_mailbox"""
    queryset = models.MailBox.objects.filter(category='mailbox')
    serializer_class = serializers.MailBoxUnreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user_id', 'from_user_id', 'sys_id', 'org_id', 'biz_id', 'obj_id', 'is_read', 'obj_type',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.filter(category='mailbox', user_id=request.user.pk, is_read=False).count()
        return Response(self.serializer_class({'count': count}).data)


class MailBoxMarkAllReadView(viewsets.GenericViewSet):
    """标记所有消息为已读 notice_mailbox"""
    queryset = models.MailBox.objects.filter(category='mailbox')
    serializer_class = serializers.MailBoxMarkAllReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        qs = models.MailBox.objects.filter(category='mailbox', user_id=request.user.pk, is_read=False)
        count = qs.count()
        qs.update(is_read=True)
        return Response(self.serializer_class({'count': count}).data)


class NoticePoolViewSet(viewsets.ModelViewSet):
    """通知池API notice_notice_pool"""
    queryset = models.NoticePool.objects.all()
    serializer_class = serializers.NoticePoolSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.NoticePoolFilterSet
