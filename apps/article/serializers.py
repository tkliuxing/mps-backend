from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from . import models


class ArticleSerializer(ModelSerializer):
    next_article = serializers.SerializerMethodField()
    prev_article = serializers.SerializerMethodField()
    create_user_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Article
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'category',
            'category_name',
            'title',
            'create_time',
            'create_user',
            'create_user_name',
            'content',
            'cover_image',
            'next_article',
            'prev_article',
        )

    def get_next_article(self, obj):
        pk = getattr(obj, 'next_article', None)
        if pk is None:
            next_article = models.Article.objects.filter(create_time__gt=obj.create_time, category=obj.category)
            if next_article:
                pk = next_article.order_by('create_time').first().pk
        return pk

    def get_prev_article(self, obj):
        pk = getattr(obj, 'prev_article', None)
        if pk is None:
            prev_article = models.Article.objects.filter(create_time__lt=obj.create_time, category=obj.category)
            if prev_article:
                pk = prev_article.order_by('-create_time').first().pk
        return pk

    def get_create_user_name(self, obj):
        if obj.create_user:
            return obj.create_user.full_name or ''
        else:
            return ''
