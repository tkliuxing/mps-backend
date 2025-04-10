from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api


router = DefaultRouter()

router.register(r'article', api.ArticleViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
)
