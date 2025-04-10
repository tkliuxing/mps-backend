from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api


router = DefaultRouter()

router.register(r'system', api.SystemViewSet)
router.register(r'systemorg', api.SystemOrgViewSet)
router.register(r'systemorgperms', api.SystemOrgPermissionsViewSet)
router.register(r'systembiz', api.SystemBizViewSet)
router.register(r'smsconfig', api.SMSConfigViewSet)
router.register(r'emailconfig', api.EmailConfigViewSet)
router.register(r'wechatconfig', api.WechatConfigViewSet)
router.register(r'systemproject', api.SystemProjectViewSet)
router.register(r'systemprojectrouter', api.SystemProjectRouterViewSet)
router.register(r'systempr', api.SystemPRViewSet)
router.register(r'systemprmove', api.SystemPRMoveView)
router.register(r'systempm', api.SystemPMViewSet)
router.register(r'systempmmove', api.SystemPMMoveView)
router.register(r'mysystempm', api.MySystemPMViewSet)
router.register(r'systemlog', api.SystemLogViewSet)
router.register(r'systemdatabackup', api.SystemDataBackupViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
)
