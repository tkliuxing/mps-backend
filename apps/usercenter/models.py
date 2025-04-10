from utility.db_fields import TableNamePKField

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    UnicodeUsernameValidator,
    send_mail,
)
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class DataPermissions:
    SELF = '仅自己'
    DEP = '本部门'
    DEP_CHILD = '本部门及下级'
    ALL = '全部'


DATA_PERMISSIONS = (
    (DataPermissions.SELF, DataPermissions.SELF),
    (DataPermissions.DEP, DataPermissions.DEP),
    (DataPermissions.DEP_CHILD, DataPermissions.DEP_CHILD),
    (DataPermissions.ALL, DataPermissions.ALL),
)


# 功能权限
class FuncPermission(MPTTModel):
    id = TableNamePKField('perm')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    name = models.CharField('名称', max_length=255)
    codename = models.CharField('说明', max_length=100, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name='上级',
                            db_index=True, on_delete=models.CASCADE, help_text='parent_id to usercenter_funcpermission')
    creator = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True, help_text='创建人', db_constraint=False, related_name='+'
    )

    class Meta:
        verbose_name = '04.功能权限'
        verbose_name_plural = verbose_name
        ordering = ('name',)

    def __str__(self):
        return "%s | %s" % (
            self.name,
            self.codename
        )


# 角色
class FuncGroup(models.Model):
    id = TableNamePKField('group')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    name = models.CharField('角色名称', max_length=150)
    sort_num = models.IntegerField('排序编号', help_text='排序编号', null=True, blank=True, default=0, db_index=True)
    permissions = models.ManyToManyField(
        FuncPermission,
        verbose_name='功能权限',
        blank=True,
        help_text="通过中间表 usercenter_funcgroup_permissions 关联 usercenter_funcpermission",
        db_constraint=False
    )

    class Meta:
        verbose_name = '03.角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 用户控制器
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.password_date = user.create_time
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, password, **extra_fields)


# 用户模型
class User(AbstractBaseUser):
    id = TableNamePKField('user')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        '用户名', max_length=150,
        help_text='必填，小于150个字符。',
        validators=[username_validator],
        error_messages={'unique': "用户名已存在。"},
    )
    password_date = models.DateTimeField('密码修改时间', null=True, blank=True, help_text='密码修改时间')
    full_name = models.CharField('姓名', max_length=30, blank=True, help_text='姓名')
    email = models.EmailField('Email', null=True, blank=True, help_text='Email')
    mobile = models.CharField('手机号码', max_length=32, null=True, blank=True, db_index=True, help_text='手机号码')
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField('可进入后台管理', default=False, help_text='可进入后台管理')
    is_active = models.BooleanField('允许登录', default=True, help_text='允许登录')
    is_tester = models.BooleanField('测试用户', default=False, help_text='测试用户')
    description = models.TextField('备注', null=True, blank=True, help_text='备注')
    department = models.ForeignKey('Department', null=True, blank=True, related_name='users',
                                   on_delete=models.SET_NULL, verbose_name='部门',
                                   help_text='department_id', db_constraint=False)
    is_department_manager = models.BooleanField('部门主管', default=False, help_text='部门主管')
    sort_num = models.IntegerField('排序编号', help_text='排序编号', null=True, blank=True, default=0, db_index=True)
    category = models.ManyToManyField(
        'baseconfig.BaseTree', blank=True, verbose_name='分类', related_name='users',
        help_text='通过中间表 usercenter_user_category 关联 baseconfig_basetree', db_constraint=False
    )
    create_time = models.DateTimeField('创建时间', auto_now=True, help_text='创建时间')
    status = models.CharField('审核状态', max_length=8, default='已通过')
    avatar = models.TextField('头像URL', null=True, blank=True, help_text='头像URL')
    sign_file = models.TextField('签名URL', null=True, blank=True, help_text='签名URL')

    # 微信相关
    wechart_name = models.CharField('微信名称', max_length=64, null=True, blank=True, db_index=True, help_text='微信名称')
    wechart_avatar = models.ImageField('微信头像', upload_to='avatar/%Y/%m/%d/', null=True, blank=True, help_text='微信头像')
    wechart_oid = models.CharField('微信OID', max_length=64, null=True, blank=True, db_index=True, help_text='微信OID')
    wechart_uid = models.CharField('微信UID', max_length=64, null=True, blank=True, db_index=True, help_text='微信UID')
    wxa_oid = models.CharField('微信小程序OID', max_length=64, null=True, blank=True, db_index=True, help_text='微信小程序OID')
    wechart_access_token = models.CharField(
        '微信 ACCESS TOKEN', max_length=128, null=True, blank=True, help_text='微信 ACCESS TOKEN'
    )
    wechart_refresh_token = models.CharField(
        '微信 REFRESH TOKEN', max_length=128, null=True, blank=True, help_text='微信 REFRESH TOKEN'
    )
    wechart_session_key = models.CharField(
        '微信会话密钥 SESSION_KEY', max_length=255, null=True, blank=True, help_text='微信会话密钥 SESSION_KEY'
    )
    data_permission = models.CharField(
        '数据范围', max_length=32, choices=DATA_PERMISSIONS, null=True, blank=True, help_text='数据范围'
    )

    func_groups = models.ManyToManyField(
        FuncGroup,
        verbose_name='角色',
        blank=True,
        help_text='通过中间表 usercenter_user_func_groups 关联 usercenter_funcgroup',
        related_name="user_set",
        related_query_name="user",
        db_constraint=False,
    )
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='网站管理角色',
        blank=True,
    )
    func_user_permissions = models.ManyToManyField(
        FuncPermission,
        verbose_name='功能权限',
        blank=True,
        help_text='通过中间表 usercenter_user_func_user_permissions 关联 usercenter_funcpermission',
        related_name="user_set",
        related_query_name="user",
        db_constraint=False,
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['sys_id']

    class Meta:
        verbose_name = '02.用户'
        verbose_name_plural = verbose_name
        unique_together = ['username', 'sys_id']
        ordering = ['department', 'sort_num', '-pk']

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    @property
    def first_name(self):
        return self.full_name

    @property
    def last_name(self):
        return self.full_name

    @property
    def user_permissions(self):
        return self.func_user_permissions.all()

    def get_group_permissions(self, obj=None):
        if self.is_superuser:
            return FuncPermission.objects.all()
        return self.func_user_permissions.all()

    @property
    def category_names(self):
        return ",".join(self.category.all().values_list('name', flat=True))

    def email_user(self, subject, message, from_email=None, **kwargs):
        if self.email:
            send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.full_name

    def move_to(self, target, position):
        users = target.department.users.exclude(pk=self.pk).values_list('pk', flat=True).order_by('sort_num', '-pk')
        users = list(users)
        try:
            target_index = users.index(target.pk)
        except ValueError:
            return
        if position == 'left':
            users = users[:target_index] + [self.pk] + users[target_index:]
        elif position == 'right':
            users = users[:target_index + 1] + [self.pk] + users[target_index + 1:]
        else:
            return
        for index, uid in enumerate(users):
            User.objects.filter(pk=uid).update(sort_num=index)

    def get_permissions(self):
        return self.func_user_permissions.all().union(
            FuncPermission.objects.filter(pk__in=self.func_groups.all().values('permissions').distinct())
        )

    @property
    def func_names(self):
        return list(self.get_permissions().values_list('name', flat=True))

    @property
    def func_codenames(self):
        return list(self.get_permissions().values_list('codename', flat=True))

    @property
    def func_group_names(self):
        return list(self.func_groups.values_list('name', flat=True))

    def has_perm(self, perm, obj=None):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        perms_codes = self.func_codenames
        if perm in perms_codes:
            return True
        return False

    def has_perms(self, perm_list, obj=None):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        perms_codes = self.func_codenames
        hp = True
        for p in perm_list:
            if p not in perms_codes:
                hp = False
        return hp

    def has_module_perms(self, app_label):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        return False

    @property
    def department_child_ids(self) -> str:
        leader_dep_qs = Department.objects.filter(head_leader=self)
        self_dep_qs = Department.objects.filter(pk=self.department.pk)  # type: ignore
        qs = self.dep_manager.all().union(self_dep_qs, leader_dep_qs)  # type: ignore
        qs = Department.objects.get_queryset_descendants(  # type: ignore
            Department.objects.filter(pk__in=qs.values('pk')),
            include_self=True
        ).order_by('tree_id', 'lft')
        return ",".join(qs.values_list('pk', flat=True))

    @property
    def department_managers(self):
        if self.department:
            return self.department.department_managers
        else:
            return []


# 机构部门模型
class Department(MPTTModel):
    id = TableNamePKField('dep')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    name = models.CharField('名称', max_length=50, help_text='名称')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name='上级',
                            db_index=True, on_delete=models.CASCADE, help_text='parent_id to usercenter_department')
    category = models.CharField('类别', max_length=15, default='', blank=True)
    contact_name = models.CharField('联系人', max_length=16, null=True, blank=True, help_text='联系人')
    contact_phone = models.CharField('联系电话', max_length=32, null=True, blank=True, help_text='联系电话')
    contact_mobile = models.CharField('手机号', max_length=32, null=True, blank=True, help_text='手机号')
    contact_fax = models.CharField('传真', max_length=32, null=True, blank=True, help_text='传真')
    description = models.TextField('说明', null=True, blank=True, help_text='说明')
    head_leader = models.ForeignKey(
        'User', on_delete=models.SET_NULL, related_name='+', db_constraint=False,
        null=True, blank=True, help_text='部门分管领导'
    )
    dep_manager = models.ManyToManyField(
        'User', related_name='dep_manager', db_constraint=False,
        blank=True, help_text='部门主管'
    )

    class Meta:
        verbose_name = '01.机构部门'
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_dep_path_name(self):
        names = self.get_ancestors(include_self=True).values_list('name', flat=True)
        return "/".join(names)

    @property
    def department_managers(self):
        managers = self.dep_manager.all()
        user_managers = User.objects.filter(department=self, is_department_manager=True)
        return managers.union(user_managers)


# 手机验证码
class PhoneAccess(models.Model):
    id = TableNamePKField('pa')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    phone = models.CharField('手机号码', max_length=30, help_text='手机号码')
    phone_access = models.CharField('验证码', max_length=10, help_text='验证码')
    create_time = models.DateTimeField('发送时间', auto_now=True, help_text='发送时间')

    class Meta:
        verbose_name = '05.手机验证码'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


# 邮箱验证码
class EmailAccess(models.Model):
    id = TableNamePKField('ea')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    email = models.EmailField('邮箱', max_length=255, help_text='邮箱')
    email_access = models.CharField('验证码', max_length=10, help_text='验证码')
    create_time = models.DateTimeField('发送时间', auto_now=True, help_text='发送时间', db_index=True)

    class Meta:
        verbose_name = '06.邮箱验证码'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
