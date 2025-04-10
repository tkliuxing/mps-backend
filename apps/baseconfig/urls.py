from django.urls import path, include
from rest_framework import routers

from . import api

router = routers.DefaultRouter()
router.register(r'flatbasetree', api.FlatBaseTreeViewSet)
router.register(r'basetree', api.BaseTreeViewSet)
router.register(r'basetreemove', api.BaseTreeMoveView)
router.register(r'basetreecopy', api.BaseTreeCopyView)
router.register(r'fileupload', api.BaseConfigFileUploadViewSet)
router.register(r'filefind', api.BaseConfigFileFindViewSet)


urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)
