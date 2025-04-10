from django.db.models import OuterRef, Subquery
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from . import serializers
from . import models


class ArticleViewSet(ModelViewSet):
    """文章API article_article"""
    queryset = models.Article.objects.order_by('-create_time')
    serializer_class = serializers.ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_fields = ('category', 'sys_id', 'org_id', 'biz_id', 'create_user',)
    search_fields = ('title',)

    def get_queryset(self):
        qs = super().get_queryset()
        next_article = qs.filter(
            create_time__gt=OuterRef('create_time')
        ).order_by('create_time')
        prev_article = qs.filter(
            create_time__lt=OuterRef('create_time')
        ).order_by('-create_time')
        return qs.annotate(
            next_article=Subquery(next_article.values('id')[:1]),
            prev_article=Subquery(prev_article.values('id')[:1]),
        )
