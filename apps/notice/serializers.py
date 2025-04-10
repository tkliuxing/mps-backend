from django.utils import timezone

from rest_framework import serializers
from usercenter.serializers import UserSerializer
from usercenter.models import User

from . import models


class NoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.MailBox
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'title',
            'content',
            'is_published',
            'publish_date',
            'create_time',
            'last_modify',
            'user',
            'msg_type',
            'obj_type',
            'obj_id',
            'is_public',
            'public_user',
            'departments',
            'department_range',
        )


class MailBoxSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(read_only=True, source='user.full_name')
    user_department_name = serializers.CharField(read_only=True, source='user.department.name')
    from_user_full_name = serializers.CharField(read_only=True, source='from_user.full_name')

    class Meta:
        model = models.MailBox
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'title',
            'content',
            'create_time',
            'is_read',
            'user',
            'msg_type',
            'obj_type',
            'obj_id',
            'user_full_name',
            'user_department_name',
            'from_user',
            'from_user_full_name',
        )

    def create(self, validated_data):
        validated_data['category'] = 'mailbox'
        return super().create(validated_data)


class NoticePoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NoticePool
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'obj_id',
            'obj_type',
            'msg_type',
            'title',
            'content',
            'send_time',
            'is_circulation',
            'circulation_time',
            'from_user',
            'is_public',
            'create_time',
            'last_modify',
            'channel',
            'send_to',
        )

    def validate(self, attr):
        # 配置默认值
        attr['is_sent'] = False
        # 添加发送用户的用户名称
        from_user = attr.get('from_user')
        if from_user:
            attr['from_user_display'] = from_user.full_name
        # 当发送时间为空时，默认设置为当前时间
        if not attr.get('send_time'):
            attr['send_time'] = timezone.now()
        return attr


class MailBoxBulkCreateSerializer(serializers.ModelSerializer):
    users = serializers.CharField(
        label='发送给', allow_null=False, allow_blank=False
    )

    class Meta:
        model = models.MailBox
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'title',
            'content',
            'create_time',
            'users',
            'from_user',
            'msg_type',
            'obj_type',
            'obj_id',
        )

    def validate(self, attr):
        users = attr['users']
        sys_id = attr['sys_id']
        ulist = []
        for uid in users.split(','):
            try:
                user = User.objects.get(pk=uid, sys_id=sys_id)
                ulist.append(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(f'user id {uid} not found!')
        attr['users'] = ulist
        return attr

    def create(self, validated_data):
        validated_data['category'] = 'mailbox'
        users = validated_data.pop('users')
        mails = []
        for user in users:
            validated_data['user'] = user
            mails.append(super().create(validated_data))
        return mails


class MailBoxUnreadSerializer(serializers.Serializer):
    count = serializers.IntegerField(label='未读消息数量', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class MailBoxMarkAllReadSerializer(serializers.Serializer):
    count = serializers.IntegerField(label='标记已读消息数量', read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
