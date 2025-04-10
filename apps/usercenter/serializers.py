from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from django.core.cache import caches
from rest_captcha import utils
from rest_captcha.settings import api_settings

from system.models import SystemOrg
from . import models

cache = caches[api_settings.CAPTCHA_CACHE]


class ChangePwdSerializer(serializers.Serializer):
    """修改密码"""
    password = serializers.CharField(label='原密码', max_length=128)
    new_password = serializers.CharField(label='新密码', max_length=128)

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError("原密码不正确")
        return value

    def save(self, **kwargs):
        self.instance.set_password(self.initial_data.get('new_password'))
        self.instance.password_date = timezone.now()
        self.instance.save()
        return self.instance

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class GroupUserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = models.User
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'username',
            'full_name',
            'department_name',
            'is_department_manager',
        )


class FuncPermissionSerializer(serializers.ModelSerializer):

    def validate_creator(self, value):
        if value is None:
            return self.context['request'].user
        return value

    class Meta:
        model = models.FuncPermission
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'name',
            'codename',
            'parent',
            'creator',
        )


class FuncPermissionTreeSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    def validate_creator(self, value):
        if value is None:
            return self.context['request'].user
        return value

    class Meta:
        model = models.FuncPermission
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'name',
            'codename',
            'parent',
            'items',
            'creator',
            'tree_id',
            'lft',
            'rght',
            'is_leaf_node',
        )

    def get_items(self, obj):
        children = obj.children.all()
        childrens = FuncPermissionTreeSerializer(children, many=True).data
        result = []
        result.extend(childrens)
        return result or None


class FuncGroupSerializer(serializers.ModelSerializer):
    """权限组"""
    user = GroupUserSerializer(source='user_set', many=True, read_only=True)
    permissions_name = serializers.SerializerMethodField()

    class Meta:
        model = models.FuncGroup
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'name',
            'sort_num',
            'user',
            'permissions',
            'permissions_name',
        )

    def get_permissions_name(self, obj):
        return list(obj.permissions.all().values_list('name', flat=True))


class FuncGroupMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FuncGroup
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'name',
        )


class DepartmentSerializer(serializers.ModelSerializer):
    """机构部门"""
    items = serializers.SerializerMethodField()

    class Meta:
        model = models.Department
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'name',
            'parent',
            'category',
            'contact_name',
            'contact_phone',
            'contact_mobile',
            'contact_fax',
            'description',
            'head_leader',
            'items',
            'level',
            'dep_manager',
        )

    def get_items(self, obj):
        children = obj.children.all()
        childrens = DepartmentSerializer(children, many=True).data
        result = []
        result.extend(childrens)
        return result


class TxlUserSerializer(serializers.ModelSerializer):
    """通讯录"""
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = models.User
        fields = (
            'id',
            'name',
            'type',
            'is_department_manager',
            'avatar',
        )

    def get_type(self, obj):
        return 'user'


class TxlSerializer(serializers.ModelSerializer):
    """通讯录"""
    type = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.Department
        fields = (
            'id',
            'name',
            'children',
            'type',
        )

    def get_children(self, obj: models.Department):
        children = obj.children.all()
        childrens = TxlSerializer(children, many=True).data
        result = []
        result.extend(childrens)
        users = obj.users.order_by('sort_num', 'full_name')
        result.extend(TxlUserSerializer(users, many=True).data)
        return result

    def get_type(self, obj):
        return 'department'


class FlatDepartmentSerializer(serializers.ModelSerializer):
    """机构部门"""

    class Meta:
        model = models.Department
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'name',
            'parent',
            'category',
            'contact_name',
            'contact_phone',
            'contact_mobile',
            'contact_fax',
            'description',
            'head_leader',
            'level',
            'dep_manager',
        )


class UserSerializer(serializers.ModelSerializer):
    """用户"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = models.User
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'username',
            'last_login',
            'full_name',
            'email',
            'mobile',
            'is_superuser',
            'is_staff',
            'is_active',
            'is_tester',
            'description',
            'department',
            'department_name',
            'department_child_ids',
            'is_department_manager',
            'sort_num',
            'category',
            'func_user_permissions',
            'func_names',
            'func_codenames',
            'func_groups',
            'func_group_names',
            'category',
            'category_names',
            'wechart_oid',
            'wechart_uid',
            'wxa_oid',
            'status',
            'data_permission',
            'avatar',
            'sign_file',
            # 'workflowrole',
        )


class MyinfoSerializer(UserSerializer):
    need_reset_password = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = UserSerializer.Meta.fields + ('need_reset_password',)

    def get_need_reset_password(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        from system.models import System
        try:
            sys = System.objects.get(sys_id=obj.sys_id)
        except System.DoesNotExist:
            return False
        if getattr(sys, 'need_reset_passwd', False) is False:
            return False
        reset_interval = getattr(sys, 'reset_passwd_interval', 90)
        if obj.password_date is None:
            return True
        if (obj.password_date + timedelta(days=reset_interval)) < timezone.now():
            return True
        return False


class UserMinSerializer(serializers.ModelSerializer):
    """用户"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = models.User
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'username',
            'last_login',
            'full_name',
            'email',
            'mobile',
            'is_staff',
            'is_active',
            'is_tester',
            'department',
            'department_name',
            'is_department_manager',
            # 'func_names',
            # 'func_group_names',
            'data_permission',
            'avatar',
            'sign_file',
        )


class UserFindSerializer(serializers.Serializer):
    sys_id = serializers.IntegerField(required=True, help_text='系统ID')
    org_id = serializers.IntegerField(required=True, help_text='机构ID')
    search = serializers.CharField(required=True, help_text='搜索串（检索姓名和手机号）')

    count = serializers.IntegerField(read_only=True, help_text='查找到的数量')
    pk = serializers.CharField(read_only=True, help_text='UID')
    username = serializers.CharField(read_only=True, help_text='用户名')
    department = serializers.CharField(read_only=True, help_text='部门ID')
    department_name = serializers.CharField(read_only=True, help_text='部门名称')
    wechart_oid = serializers.CharField(read_only=True, help_text='微信OpenID')
    full_name = serializers.CharField(read_only=True, help_text='姓名')
    mobile = serializers.CharField(read_only=True, help_text='手机号')

    def create(self, validated_data):
        users = models.User.objects.filter(
            sys_id=validated_data['sys_id'],
            org_id=validated_data['org_id'],
        ).filter(
            Q(full_name=validated_data['search']) | Q(mobile=validated_data['search'])
        )
        if users:
            count = users.count()
            if count > 1:
                return {'count': count}
            user = users[0]
            return {
                'count': count,
                'pk': user.pk,
                'username': user.username,
                'department': user.department_id or '',
                'department_name': user.department.name if user.department else '',
                'wechart_oid': user.wechart_oid,
                'full_name': user.full_name,
                'mobile': user.mobile,
            }
        return {'count': 0}

    def update(self, instance, validated_data):
        return instance


class DepartmentMoveSerializer(serializers.Serializer):
    POSITION_CHOICES = (
        ('first-child', '第一个子部门'),
        ('last-child', '最后一个子部门'),
        ('left', '之前'),
        ('right', '之后'),
    )
    department = serializers.CharField(
        label='当前部门ID',
        help_text='当前部门ID'
    )
    target = serializers.CharField(
        label='目标部门ID',
        help_text='目标部门ID'
    )
    position = serializers.ChoiceField(
        label='位置',
        help_text='位置',
        choices=POSITION_CHOICES
    )

    def update(self, instance, validated_data):
        target = models.Department.objects.get(pk=validated_data['target'])
        instance.move_to(target, validated_data['position'])
        return instance

    def create(self, validated_data):
        department = models.Department.objects.get(pk=validated_data['department'])
        target = models.Department.objects.get(pk=validated_data['target'])
        department.move_to(target, validated_data['position'])
        return department


class UserPhoneRegSerializer(serializers.ModelSerializer):
    """用户手机号注册"""
    phone_access = serializers.CharField(required=True, write_only=True, help_text='验证码')
    captcha_key = serializers.CharField(max_length=64, write_only=True)
    captcha_value = serializers.CharField(max_length=8, trim_whitespace=True, write_only=True)
    mobile = serializers.CharField(required=True, label='手机号必填')

    class Meta:
        model = models.User
        fields = (
            'phone_access',
            'captcha_key',
            'captcha_value',
            'pk',
            'sys_id',
            'org_id',
            'username',
            'full_name',
            'email',
            'mobile',
            'wechart_oid',
            'wxa_oid',
            'status',
        )

    def validate(self, data):
        phone, pa, sys_id, username = data['mobile'], data['phone_access'], data['sys_id'], data['username']
        try:
            access = models.PhoneAccess.objects.get(phone=phone, phone_access=pa, sys_id=sys_id)
            if phone != '17704818161':
                access.delete()
        except models.PhoneAccess.DoesNotExist:
            raise ValidationError('手机验证码错误')
        if models.User.objects.filter(username=username, sys_id=sys_id):
            raise ValidationError('该用户已存在！')
        del data['phone_access']
        data = super(UserPhoneRegSerializer, self).validate(data)

        cache_key = utils.get_cache_key(data['captcha_key'])

        if data['captcha_key'] in api_settings.MASTER_CAPTCHA:
            real_value = api_settings.MASTER_CAPTCHA[data['captcha_key']]
        else:
            real_value = cache.get(cache_key)

        if real_value is None:
            raise serializers.ValidationError('验证码错误')

        cache.delete(cache_key)
        if data['captcha_value'].upper() != real_value:
            raise serializers.ValidationError('验证码错误')

        del data['captcha_key']
        del data['captcha_value']
        return data


class UserCaptchaRegSerializer(serializers.ModelSerializer):
    """用户图片验证码注册"""
    captcha_key = serializers.CharField(max_length=64, write_only=True)
    captcha_value = serializers.CharField(max_length=8, trim_whitespace=True, write_only=True)
    password = serializers.CharField(
        max_length=128, write_only=True, trim_whitespace=True
    )
    is_active = serializers.BooleanField(
        read_only=True
    )

    class Meta:
        model = models.User
        fields = (
            'captcha_key',
            'captcha_value',
            'pk',
            'sys_id',
            'org_id',
            'username',
            'last_login',
            'full_name',
            'email',
            'mobile',
            'department',
            'wechart_oid',
            'wxa_oid',
            'password',
            'is_active',
            'status',
            'is_tester',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=models.User.objects.all(),
                fields=['username', 'sys_id'],
                message='此用户已注册'
            )
        ]

    def validate(self, data):
        phone, sys_id, username = data['mobile'], data['sys_id'], data['username']
        if models.User.objects.filter(username=username, sys_id=sys_id):
            raise ValidationError('该用户已存在！')

        data = super(UserCaptchaRegSerializer, self).validate(data)
        cache_key = utils.get_cache_key(data['captcha_key'])

        if data['captcha_key'] in api_settings.MASTER_CAPTCHA:
            real_value = api_settings.MASTER_CAPTCHA[data['captcha_key']]
        else:
            real_value = cache.get(cache_key)

        if real_value is None:
            raise serializers.ValidationError('验证码错误')

        cache.delete(cache_key)
        if data['captcha_value'].upper() != real_value:
            raise serializers.ValidationError('验证码错误')

        del data['captcha_key']
        del data['captcha_value']
        return data


class OrgUserCaptchaRegSerializer(UserCaptchaRegSerializer):
    org_name = serializers.CharField(max_length=256, required=True, write_only=True, help_text='组织名称')
    org_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.User
        fields = (
            'captcha_key',
            'captcha_value',
            'pk',
            'sys_id',
            'org_id',
            'username',
            'last_login',
            'full_name',
            'email',
            'mobile',
            'department',
            'wechart_oid',
            'wxa_oid',
            'password',
            'is_active',
            'status',
            'is_tester',
            'org_name',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=models.User.objects.all(),
                fields=['username', 'sys_id'],
                message='此用户已注册'
            ),
        ]

    def validate(self, data):
        org_name = data['org_name']
        sys_id = data['sys_id']
        org = SystemOrg.objects.filter(sys_id=sys_id, name=org_name)
        if org:
            raise ValidationError('机构已注册')
        return super(OrgUserCaptchaRegSerializer, self).validate(data)

    def create(self, validated_data):
        org = SystemOrg.create_from_sys_id_and_name(validated_data['sys_id'], validated_data['org_name'])
        validated_data['org_id'] = org.org_id
        del validated_data['org_name']
        instance = super(OrgUserCaptchaRegSerializer, self).create(validated_data)
        department = models.Department.objects.filter(sys_id=instance.sys_id, org_id=instance.org_id).first()
        if department:
            instance.department = department
            instance.save()
        default_org_permissions = org.permissions.all()
        instance.func_user_permissions.set(list(default_org_permissions))
        return instance


class UserPhoneCheckSerializer(serializers.Serializer):
    exist = serializers.BooleanField(read_only=True, help_text='是否存在')
    phone = serializers.CharField(required=True, max_length=11, help_text='手机号')
    sys_id = serializers.IntegerField(required=True, help_text='sys id')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
