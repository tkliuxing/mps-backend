from django.db.models import Q
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from usercenter.serializers import FuncPermissionSerializer
from . import models


class SystemSerializer(ModelSerializer):
    permissions = FuncPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = models.System
        fields = (
            'pk',
            'sys_id',
            'name',
            'url',
            'permissions',
            'default_org_permissions',
            'multi_org',
            'description',
            'create_time',
            'update_time',
            'allow_org_register',
            'default_org_validity_period',
            'is_long_time_validity_period',
            'industry',
            'need_reset_passwd',
            'reset_passwd_interval',
            'log_level',
        )


class SystemOrgSerializer(ModelSerializer):

    class Meta:
        model = models.SystemOrg
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'src_id',
            'system',
            'name',
            'end_date',
            'manager',
            'create_time',
            'license',
            'permissions',
            'permissions_display',
            'allow_user_register',
            'is_disabled',
        )
        read_only_fields = ['org_id', 'src_id']

    def create(self, validated_data):
        from usercenter.models import Department
        instance = super().create(validated_data)  # type: models.SystemOrg
        Department.objects.create(
            name=instance.name,
            sys_id=instance.sys_id,
            org_id=instance.org_id
        )
        instance.copy_basetree_root()
        instance.permissions.set(list(instance.system.permissions.all()))
        return instance


class SystemBizSerializer(ModelSerializer):

    class Meta:
        model = models.SystemBiz
        fields = (
            'pk',
            'sys_id',
            'biz_id',
            'system',
            'name',
        )

    def validate(self, attrs):
        biz_id = attrs['biz_id']
        system = attrs['system']  # type: models.System
        if not self.instance and system.bizs.filter(biz_id=biz_id):
            raise serializers.ValidationError('biz_id 重复！')
        return attrs


class SMSConfigSerializer(ModelSerializer):
    class Meta:
        model = models.SMSConfig
        fields = (
            'pk',
            'system',
            'name',
            'sms_type',
            'sms_type_display',
            'is_enabled',
            'post_url',
            'app_key',
            'app_id',
            'template_id',
            'template_sign',
            'tencent_cloud_appid',
            'tencent_cloud_secretid',
            'tencent_cloud_secretkey',
        )


class WechatConfigSerializer(ModelSerializer):

    class Meta:
        model = models.WechatConfig
        fields = (
            'pk',
            'system',
            'system_org',
            'is_default',
            'mp_name',
            'mp_aid',
            'mp_sk',
            'wxa_name',
            'wxa_aid',
            'wxa_sk',
            'mch_api_key',
            'mch_id',
            'mch_sub_id',
            'mch_cert',
            'mch_key',
            'create_time',
        )


class SystemProjectSerializer(ModelSerializer):
    sys_id = serializers.IntegerField(read_only=True, source='system.sys_id')

    class Meta:
        model = models.SystemProject
        fields = (
            'pk',
            'sys_id',
            'biz_id',
            'system',
            'name',
            'pm_name',
            'git_url',
            'project_type',
            'desc',
            'router_content',
            'online_time',
            'create_time',
        )


class SystemProjectRouterSerializer(ModelSerializer):
    class Meta:
        model = models.SystemProject
        fields = (
            'pk',
            'router_content',
        )


class SystemPRSerializer(ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.SystemProjectRouter
        fields = (
            'pk',
            'sys_id',
            'project',
            'parent',
            'children',
            'path',
            'title',
            'name',
            'component',
            'redirect',
            'props',
            'alias',
            'meta',
            'permission',
            'permission_name',
            'is_leaf_node',
        )

    def get_child_serializer_data(self, children):
        return SystemPRSerializer(children, many=True).data

    def get_children(self, obj):
        children = obj.children.all()
        childrens = self.get_child_serializer_data(children)
        result = []
        result.extend(childrens)
        return result or None


class SystemPRMoveSerializer(serializers.Serializer):
    POSITION_CHOICES = (
        ('first-child', '第一个子节点'),
        ('last-child', '最后一个子节点'),
        ('left', '之前'),
        ('right', '之后'),
    )
    node = serializers.CharField(
        label='当前节点ID',
        help_text='当前节点ID'
    )
    target = serializers.CharField(
        label='目标节点ID',
        help_text='目标节点ID'
    )
    position = serializers.ChoiceField(
        label='位置',
        help_text='位置',
        choices=POSITION_CHOICES
    )

    def validate(self, attrs):
        try:
            node = models.SystemProjectRouter.objects.get(pk=attrs['node'])
        except models.SystemProjectRouter.DoesNotExist:
            raise serializers.ValidationError('node 不存在')
        try:
            target = models.SystemProjectRouter.objects.get(pk=attrs['target'])
        except models.SystemProjectRouter.DoesNotExist:
            raise serializers.ValidationError('target 不存在')
        attrs['node'] = node
        attrs['target'] = target
        return attrs

    def update(self, instance, validated_data):
        target = validated_data['target']
        instance.move_to(target, validated_data['position'])
        return instance

    def create(self, validated_data):
        node = validated_data['node']
        target = validated_data['target']
        node.move_to(target, validated_data['position'])
        return node


class SystemPMSerializer(ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.SystemProjectMenu
        fields = (
            'pk',
            'sys_id',
            'project',
            'parent',
            'children',
            'name',
            'icon',
            'router_name',
            'permission',
        )

    def get_child_serializer_data(self, children):
        return SystemPMSerializer(children, many=True).data

    def get_children(self, obj):
        children = obj.children.all()
        childrens = self.get_child_serializer_data(children)
        result = []
        result.extend(childrens)
        return result


class MySystemPMSerializer(ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.SystemProjectMenu
        fields = (
            'pk',
            'sys_id',
            'project',
            'parent',
            'children',
            'name',
            'icon',
            'router_name',
            'permission',
        )

    def get_child_serializer_data(self, children):
        return SystemPMSerializer(children, many=True, context=self.context).data

    def get_children(self, obj):
        perms = self.context['view'].perms_cache
        children = obj.children.filter(
            Q(permission__in=perms) | Q(permission__isnull=True)
        )
        childrens = self.get_child_serializer_data(children)
        result = []
        result.extend(childrens)
        return result


class SystemPMMoveSerializer(serializers.Serializer):
    POSITION_CHOICES = (
        ('first-child', '第一个子节点'),
        ('last-child', '最后一个子节点'),
        ('left', '之前'),
        ('right', '之后'),
    )
    node = serializers.CharField(
        label='当前节点ID',
        help_text='当前节点ID'
    )
    target = serializers.CharField(
        label='目标节点ID',
        help_text='目标节点ID'
    )
    position = serializers.ChoiceField(
        label='位置',
        help_text='位置',
        choices=POSITION_CHOICES
    )

    def validate(self, attrs):
        try:
            node = models.SystemProjectMenu.objects.get(pk=attrs['node'])
        except models.SystemProjectMenu.DoesNotExist:
            raise serializers.ValidationError('node 不存在')
        try:
            target = models.SystemProjectMenu.objects.get(pk=attrs['target'])
        except models.SystemProjectMenu.DoesNotExist:
            raise serializers.ValidationError('target 不存在')
        attrs['node'] = node
        attrs['target'] = target
        return attrs

    def update(self, instance, validated_data):
        target = validated_data['target']
        instance.move_to(target, validated_data['position'])
        return instance

    def create(self, validated_data):
        node = validated_data['node']
        target = validated_data['target']
        node.move_to(target, validated_data['position'])
        return node


class SystemLogSerializer(ModelSerializer):
    class Meta:
        model = models.SystemLog
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'log_level',
            'log_type',
            'template_id',
            'user',
            'content',
            'user_name',
            'create_time',
        )


class SystemDataBackupSerializer(ModelSerializer):
    class Meta:
        model = models.SystemDataBackup
        fields = (
            'pk', 'sys_id', 'org_id', 'create_time', 'user_name', 'backup_params', 'backup_file',
        )

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.create_backup_file()
        return instance


class EmailConfigSerializer(ModelSerializer):
    class Meta:
        model = models.EmailConfig
        fields = (
            'pk',
            'system',
            'system_org',
            'name',
            'host',
            'port',
            'username',
            'password',
            'use_ssl',
            'use_tls',
            'from_email',
            'from_name'
        )
