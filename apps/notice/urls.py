from django.urls import path, include
from rest_framework import routers

from . import api

router = routers.DefaultRouter()
router.register(r'notice', api.NoticeViewSet)
router.register(r'view-my-notice', api.ViewMyNoticeViewSet)
router.register(r'mailbox', api.MailBoxViewSet)
router.register(r'mailboxbulkcreate', api.MailBoxBulkCreateViewSet)
router.register(r'mailbox-mark-all-read', api.MailBoxMarkAllReadView)
router.register(r'mailbox-unread-count', api.MailBoxUnreadCountView)
router.register(r'noticepool', api.NoticePoolViewSet)


urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)
