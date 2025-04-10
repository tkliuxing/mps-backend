from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api
from . import views

router = DefaultRouter()

router.register(r'gps-point', api.PointViewSet)
router.register(r'gps-point-find', api.PointFindViewSet)
router.register(r'gps-point-time', api.PointTimeViewSet)
router.register(r'gps-polygon', api.PolygonViewSet)
router.register(r'gps-lastpoints', api.LastPointViewSet)
router.register(r'gps-refreshlastpoints', api.RefreshLastPointViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
    path('api/v1/gps-test/', views.gps_test),
)
