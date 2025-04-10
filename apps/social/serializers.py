from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from usercenter.serializers import UserMinSerializer
from . import models


class SocialDynamicSerializer(ModelSerializer):
    user_info = serializers.SerializerMethodField(help_text='用户详情')
    comments = serializers.SerializerMethodField(help_text='前两条评论')
    comments_count = serializers.SerializerMethodField(help_text='评论数量')
    thumbs_up = serializers.SerializerMethodField(help_text='点赞数量')
    thumbs_up_id = serializers.SerializerMethodField(help_text='当前用户点赞ID')
    thumbs_ups = serializers.SerializerMethodField(help_text='前10哥点赞对象数组')
    is_thumbs_up = serializers.SerializerMethodField(help_text='当前用户是否点过赞')

    class Meta:
        model = models.SocialDynamic
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'user',
            'user_info',
            'publish_time',
            'content',
            'title',
            'visible',
            'is_anonymous',
            'images',
            'comments',
            'comments_count',
            'thumbs_up_id',
            'thumbs_up',
            'thumbs_ups',
            'is_thumbs_up',
            'is_hot',
            'is_pub',
        )

    def get_user_info(self, obj):
        serialize = UserMinSerializer(instance=obj.user)
        return serialize.data

    def get_comments(self, obj):
        comments = obj.comments.all().order_by('comment_time')[:2]
        serializer = SocialCommentSerializer(instance=comments, many=True)
        return serializer.data

    def get_comments_count(self, obj):
        return obj.comments.all().count()

    def get_thumbs_up(self, obj):
        return obj.thumbs_up.all().count()

    def get_thumbs_ups(self, obj):
        qs = obj.thumbs_up.all().order_by('thumbs_up_time')[:10]
        serialize = SocialPraiseSerializer(instance=qs, many=True)
        return serialize.data

    def get_is_thumbs_up(self, obj):
        if 'request' in self._context:
            user = self._context['request'].user
        else:
            return False
        return bool(models.SocialPraise.objects.filter(user=user, thumbs_up_dynamic=obj))

    def get_thumbs_up_id(self, obj):
        if 'request' in self._context:
            user = self._context['request'].user
        else:
            return None
        try:
            return models.SocialPraise.objects.get(user=user, thumbs_up_dynamic=obj).pk
        except models.SocialPraise.DoesNotExist:
            return None


class SocialCommentSerializer(ModelSerializer):
    user_full_name = serializers.SerializerMethodField(required=False)
    be_commented_full_name = serializers.SerializerMethodField(required=False)
    user_info = serializers.SerializerMethodField(help_text='用户详情')

    class Meta:
        model = models.SocialComment
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'user',
            'user_info',
            'be_commented',
            'thumbs_up',
            'content',
            'comment_time',
            'associated',
            'user_full_name',
            'be_commented_full_name',
        )

    def get_be_commented_full_name(self, obj):
        return obj.be_commented.full_name or ''

    def get_user_full_name(self, obj):
        return obj.user.full_name or ''

    def get_user_info(self, obj):
        return UserMinSerializer(instance=obj.user).data


class SocialPraiseSerializer(ModelSerializer):
    full_name = serializers.SerializerMethodField(help_text='用户姓名')

    class Meta:
        model = models.SocialPraise
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'user',
            'full_name',
            'be_thumbs_up',
            'thumbs_up_dynamic',
            'thumbs_up_time',
        )

    def get_full_name(self, obj):
        return obj.user.full_name
