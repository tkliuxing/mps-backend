from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api


router = DefaultRouter()

router.register(r'parameters', api.ParametersViewSet)
router.register(r'flatparameters', api.FlatParametersViewSet)
router.register(r'parameters-categorys', api.ParametersCategorysViewSet)
router.register(r'parameters-to-basetree', api.ParametersToBaseTreeViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
)
