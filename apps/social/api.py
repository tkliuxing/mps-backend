from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from . import serializers
from . import models
from . import filters


class SocialDynamicViewSet(ModelViewSet):
    """社交动态API（朋友圈） social_socialdynamic"""
    queryset = models.SocialDynamic.objects.order_by('-publish_time')
    serializer_class = serializers.SocialDynamicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.SocialDynamicFilterSet


class SocialCommentViewSet(ModelViewSet):
    """社交动态评论API social_socialcomment"""
    queryset = models.SocialComment.objects.order_by('comment_time')
    serializer_class = serializers.SocialCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('associated', 'be_commented', 'user',)


class SocialPraiseViewSet(ModelViewSet):
    """社交动态点赞API social_socialpraise"""
    queryset = models.SocialPraise.objects.order_by('thumbs_up_time')
    serializer_class = serializers.SocialPraiseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('thumbs_up_dynamic', 'be_thumbs_up', 'user',)
