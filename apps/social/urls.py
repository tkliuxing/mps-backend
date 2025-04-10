from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api


router = DefaultRouter()

router.register(r'socialdynamic', api.SocialDynamicViewSet)
router.register(r'socialcomment', api.SocialCommentViewSet)
router.register(r'socialpraise', api.SocialPraiseViewSet)

urlpatterns = (
    path('api/v1/', include(router.urls)),
)
