import datetime
import base64
import json
import gzip
import logging
from utility.db_fields import TableNamePKField

from django.utils import timezone
from django.db import models
from django.core.files.base import ContentFile
from mptt.models import MPTTModel, TreeForeignKey

LOG_LEVELS = (
    (0, '0'),
    (1, '1'),
    (2, '2'),
)

logger = logging.getLogger('django')


# 系统
class System(models.Model):
    """系统"""
    id = TableNamePKField('SYS')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True, unique=True)
    name = models.CharField('系统名称', max_length=256, help_text='系统名称')
    url = models.CharField('线上地址', max_length=256, null=True, blank=True, help_text='线上地址')
    description = models.TextField('系统说明', null=True, blank=True, help_text='系统说明')
    multi_org = models.BooleanField('多租户系统', default=False, help_text='多租户系统')
    allow_org_register = models.BooleanField('允许租户注册', default=False, help_text='允许租户注册')
    default_org_validity_period = models.IntegerField('默认租户有效期', default=365, help_text='默认租户有效期')
    is_long_time_validity_period = models.BooleanField('长期有效', default=True, help_text='长期有效')
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    permissions = models.ManyToManyField(
        'usercenter.FuncPermission', related_name='system', verbose_name='模块权限', blank=True, db_constraint=False
    )
    default_org_permissions = models.ManyToManyField(
        'usercenter.FuncPermission', related_name='+', verbose_name='默认租户模块权限', blank=True,
        db_constraint=False
    )
    log_level = models.IntegerField('日志级别', choices=LOG_LEVELS, default=0, help_text='日志级别')
    industry = models.CharField('行业', max_length=256, null=True, blank=True, help_text='行业')
    # single_device = models.BooleanField('单设备登录', default=False, help_text='单设备登录')
    need_reset_passwd = models.BooleanField('需要定时重置密码', default=False, help_text='需要定时重置密码')
    reset_passwd_interval = models.IntegerField('重置密码周期', null=True, blank=True, help_text='重置密码周期')

    class Meta:
        verbose_name = '系统'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.sys_id}: {self.name}'


def next_org_id():
    return (SystemOrg.objects.aggregate(max_orgid=models.Max('org_id'))['max_orgid'] or 0) + 1


# 系统租户
class SystemOrg(models.Model):
    """系统租户"""
    id = TableNamePKField('SYSORG')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('租户ID', default=next_org_id, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    system = models.ForeignKey('System', on_delete=models.CASCADE, related_name='orgs', verbose_name='系统')
    name = models.CharField('名称', max_length=256, help_text='名称')
    manager = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, help_text='管理员ID', db_constraint=False,
        related_name='+'
    )
    allow_user_register = models.BooleanField('允许用户注册', default=True, help_text='允许用户注册')
    create_time = models.DateTimeField(default=timezone.now)
    license = models.TextField('证书内容', null=True, blank=True, help_text='证书内容')
    is_disabled = models.BooleanField('是否禁用', default=False, help_text='是否禁用')

    permissions = models.ManyToManyField(
        'usercenter.FuncPermission',
        verbose_name='功能权限',
        blank=True,
        help_text='通过中间表 system_systemorg_func_user_permissions 关联 usercenter_funcpermission',
        related_name="+",
        db_constraint=False,
    )

    class Meta:
        verbose_name = '系统租户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.sys_id} - {self.org_id}: {self.name}'

    @property
    def permissions_display(self) -> list:
        return list(self.permissions.all().values_list('name', flat=True))

    def end_date(self) -> datetime.date:
        import logging
        import json
        import arrow
        logger = logging.getLogger('django')
        if not self.license:
            return datetime.date.today() - datetime.timedelta(days=1)
        from .utils.crypt import base64_rsa_decrypt, PRIVATE_KEY
        try:
            data = base64_rsa_decrypt(self.license, base64.b64decode(PRIVATE_KEY).decode())
            data = json.loads(data)
            return arrow.get(data['end_date']).date()
        except Exception as e:
            logger.exception('license decrypt error!')
            return datetime.date.today() - datetime.timedelta(days=1)

    @classmethod
    def create_from_sys_id_and_name(cls, sys_id, name):
        """根据系统ID和租户名称创建租户"""
        from usercenter.models import Department
        if SystemOrg.objects.filter(name=name, sys_id=sys_id):
            raise ValueError(f'系统[{sys_id}]中已存在租户[{name}]')
        system_obj = System.objects.get(sys_id=sys_id)
        default_org_permissions = system_obj.default_org_permissions.all()
        org = cls.objects.create(sys_id=sys_id, system=system_obj, name=name)
        org.permissions.set(list(default_org_permissions))
        Department.objects.create(
            name=org.name,
            sys_id=org.sys_id,
            org_id=org.org_id
        )
        return org

    def copy_basetree_root(self):
        from baseconfig.models import BaseTree
        from utility.db_fields import gen_new_id
        last_org = self.system.orgs.order_by('org_id').first()
        if last_org is None:
            return
        last_org_id = last_org.org_id
        self_basetree_roots = list(BaseTree.objects.filter(
            org_id=self.org_id, sys_id=self.sys_id, level=0
        ).values_list('name', flat=True))
        for base_tree in BaseTree.objects.filter(org_id=last_org_id, sys_id=self.sys_id, level=0):
            if base_tree.name in self_basetree_roots:
                continue
            BaseTree.objects.create(
                id=gen_new_id('bt'),
                sys_id=self.sys_id,
                org_id=self.org_id,
                biz_id=base_tree.biz_id,
                src_id=base_tree.src_id,
                name=base_tree.name,
                description=base_tree.description,
                arguments=base_tree.arguments,
                icon=base_tree.icon,
            )


class SystemBiz(models.Model):
    """业务子系统定义"""
    id = TableNamePKField('SYSBIZ')
    sys_id = models.IntegerField('系统ID', db_index=True)
    biz_id = models.IntegerField('业务ID', db_index=True)
    system = models.ForeignKey('System', on_delete=models.CASCADE, related_name='bizs', verbose_name='系统')
    name = models.CharField('业务子系统名称', max_length=256, help_text='业务子系统名称')

    class Meta:
        verbose_name = '业务子系统定义'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.sys_id}: {self.biz_id}: {self.name}'


# 短信平台配置
class SMSConfig(models.Model):
    """短信平台配置"""
    SMS_TYPES = (
        ("JUHE", "聚合数据"),
        ("TENCENT", "腾讯云"),
        ("JHSL", "景鸿商旅"),
    )
    id = TableNamePKField('SYSSMS')
    system = models.ForeignKey(
        'System', on_delete=models.CASCADE, related_name='smsconfig',
        verbose_name='系统ID', help_text='系统ID', null=True, blank=True,
        db_constraint=False
    )
    system_org = models.ForeignKey(
        'SystemOrg', on_delete=models.CASCADE, related_name='smsconfig',
        verbose_name='系统租户ID', help_text='系统租户ID', null=True, blank=True,
        db_constraint=False
    )
    name = models.CharField('短信配置名称', max_length=128, null=True, blank=True, help_text='短信配置名称')
    sms_type = models.CharField('平台类型', max_length=32, choices=SMS_TYPES, help_text='平台类型')
    is_enabled = models.BooleanField('是否启用', default=True, help_text='是否启用')
    post_url = models.CharField('发送接口URL', max_length=255, null=True, blank=True, help_text='发送接口URL')
    app_key = models.CharField('App Key', max_length=128, null=True, blank=True, help_text='App Key')
    app_id = models.CharField('App ID', max_length=128, null=True, blank=True, help_text='App ID')
    template_id = models.CharField('短信模板ID', max_length=128, null=True, blank=True, help_text='短信模板ID')
    template_sign = models.CharField('短信模板签名', max_length=128, null=True, blank=True, help_text='短信模板签名')

    tencent_cloud_appid = models.CharField('腾讯云APPID', max_length=128, null=True, blank=True, help_text='腾讯云APPID')
    tencent_cloud_secretid = models.CharField('腾讯云SECRETID', max_length=128, null=True, blank=True,
                                              help_text='腾讯云SECRETID')
    tencent_cloud_secretkey = models.CharField('腾讯云SECRETKEY', max_length=128, null=True, blank=True,
                                               help_text='腾讯云SECRETKEY')

    class Meta:
        verbose_name = '短信平台配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}:{} - {}".format(self.system, self.get_sms_type_display(), self.name)

    @property
    def sms_type_display(self):
        return self.get_sms_type_display()


class SMSLog(models.Model):
    id = TableNamePKField('SMSL')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('租户ID', null=True, blank=True, help_text='租户ID')
    sms_config = models.ForeignKey(
        'SMSConfig', on_delete=models.SET_NULL, null=True, blank=True, help_text='短信配置', db_constraint=False,
        related_name='+'
    )
    create_time = models.DateTimeField('发送时间', auto_now_add=True)
    expire_seconds = models.IntegerField('超时时长', null=True, blank=True, help_text='超时时长')
    phone = models.CharField('手机号码', max_length=32, help_text='手机号码')
    content = models.CharField('短信内容', max_length=255, help_text='短信内容')

    class Meta:
        verbose_name = '短信发送记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}@{}:{} - {}".format(
            self.sys_id,
            self.create_time.strftime('%Y%m%d %H:%M:%S') if self.create_time else '-' * 17,
            self.phone,
            self.content
        )

    @property
    def is_expire(self):
        if self.create_time is None or self.expire_seconds is None:
            return True
        return (timezone.now() - self.create_time).seconds > self.expire_seconds


class EmailConfig(models.Model):
    """邮件平台配置"""
    id = TableNamePKField('SYSEM')
    system = models.ForeignKey(
        'System', on_delete=models.CASCADE, related_name='emailconfig',
        verbose_name='系统ID', help_text='系统ID', null=True, blank=True,
        db_constraint=False
    )
    system_org = models.ForeignKey(
        'SystemOrg', on_delete=models.CASCADE, related_name='emailconfig',
        verbose_name='系统租户ID', help_text='系统租户ID', null=True, blank=True,
        db_constraint=False
    )
    name = models.CharField('邮件配置名称', max_length=128, null=True, blank=True, help_text='邮件配置名称')
    host = models.CharField('邮件服务器', max_length=128, null=True, blank=True, help_text='邮件服务器')
    port = models.IntegerField('邮件服务器端口', null=True, blank=True, help_text='邮件服务器端口')
    username = models.CharField('邮件服务器用户名', max_length=128, null=True, blank=True, help_text='邮件服务器用户名')
    password = models.CharField('邮件服务器密码', max_length=128, null=True, blank=True, help_text='邮件服务器密码')
    use_ssl = models.BooleanField('使用SSL', default=False, help_text='使用SSL')
    use_tls = models.BooleanField('使用TLS', default=False, help_text='使用TLS')
    from_email = models.EmailField('发件人邮箱', null=True, blank=True, help_text='发件人邮箱')
    from_name = models.CharField('发件人名称', max_length=128, null=True, blank=True, help_text='发件人名称')
    title_prefix = models.CharField('标题前缀', max_length=128, null=True, blank=True, help_text='标题前缀')

    class Meta:
        verbose_name = '邮件平台配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}:{} - {}".format(self.system, self.name, self.host)


# 系统微信相关配置
class WechatConfig(models.Model):
    """系统微信相关配置"""
    id = TableNamePKField('SYSWC')
    system = models.ForeignKey(
        'System', on_delete=models.CASCADE, related_name='wechatconfig',
        verbose_name='系统ID', help_text='系统ID', null=True, blank=True,
        db_constraint=False
    )
    system_org = models.ForeignKey(
        'SystemOrg', on_delete=models.CASCADE, related_name='wechatconfig',
        verbose_name='系统租户ID', help_text='系统租户ID', null=True, blank=True,
        db_constraint=False
    )
    is_default = models.BooleanField('是否默认', default=True, help_text='是否默认')
    mp_name = models.CharField('微信公众号名称', max_length=64, null=True, blank=True, help_text='微信公众号名称')
    mp_aid = models.CharField(
        '微信公众号AppID', max_length=64, null=True, blank=True, db_index=True, help_text='微信公众号AppID')
    mp_sk = models.CharField(
        '微信公众号AppSecret', max_length=128, null=True, blank=True, db_index=True, help_text='微信公众号AppSecret')
    wxa_name = models.CharField('微信小程序名称', max_length=64, null=True, blank=True, help_text='微信小程序名称')
    wxa_aid = models.CharField(
        '微信小程序AppID', max_length=64, null=True, blank=True, db_index=True, help_text='微信小程序AppID')
    wxa_sk = models.CharField(
        '微信小程序AppSecret', max_length=128, null=True, blank=True, db_index=True, help_text='微信小程序AppSecret')
    mch_api_key = models.CharField(
        '微信支付商户key', max_length=32, null=True, blank=True, db_index=True, help_text='微信支付商户key')
    mch_id = models.CharField(
        '微信支付商户号', max_length=32, null=True, blank=True, db_index=True, help_text='微信支付商户号')
    mch_sub_id = models.CharField(
        '微信支付子商户号', max_length=32, null=True, blank=True, db_index=True, help_text='微信支付子商户号')
    mch_cert = models.CharField(
        '微信支付商户证书路径', max_length=256, null=True, blank=True, db_index=True, help_text='微信支付商户证书路径')
    mch_key = models.CharField(
        '微信支付商户证书私钥路径', max_length=256, null=True, blank=True, db_index=True, help_text='微信支付商户证书私钥路径')
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = '系统微信相关配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} - {}".format(self.system, self.pk)


# 系统项目工程配置
class SystemProject(models.Model):
    """系统项目工程配置"""
    PROJECT_TYPES = (
        ('PC WEB', 'PC WEB',),
        ('微信小程序', '微信小程序',),
        ('公众号网页', '公众号网页',),
        ('移动端H5应用', '移动端H5应用',),
        ('uni-app', 'uni-app',),
        ('react-native', 'react-native',),
        ('Python CMS', 'Python CMS',),
    )
    id = TableNamePKField('SYSP')
    biz_id = models.IntegerField('业务子系统ID', null=True, blank=True, db_index=True, help_text='业务子系统ID')
    system = models.ForeignKey(
        'System', on_delete=models.CASCADE, related_name='projects', verbose_name='系统ID', help_text='系统ID'
    )
    name = models.CharField('项目名称', max_length=63, help_text='项目名称')
    pm_name = models.CharField('项目管理名称', max_length=63, null=True, blank=True, help_text='项目管理名称')
    git_url = models.CharField('Git 地址', max_length=255, help_text='项目Git仓库地址(git remote url)', db_index=True)
    project_type = models.CharField(
        '项目工程类型', max_length=31, db_index=True, choices=PROJECT_TYPES, help_text='项目工程类型')
    desc = models.TextField('说明', null=True, blank=True, help_text='说明')
    router_content = models.TextField('路由内容', null=True, blank=True, help_text='路由内容')
    online_time = models.DateTimeField('上线时间', null=True, blank=True, help_text='上线时间')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '系统项目工程配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "SystemProject {} - {}".format(self.system, self.name)

    @property
    def git_dirname(self):
        if not self.git_url:
            return None
        return self.git_url.split('/')[-1].split('.')[0]

    @property
    def git_local_path(self):
        import os
        try:
            from coderegister.utils.gitutil import BASE_ROOT
        except ImportError:
            return None
        if not self.git_dirname:
            return None
        return os.path.join(BASE_ROOT, self.git_dirname)


# 系统项目工程路由配置
class SystemProjectRouter(MPTTModel):
    """系统项目工程路由配置"""
    id = TableNamePKField('SPR')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    project = models.ForeignKey('SystemProject', on_delete=models.CASCADE, related_name='routers', verbose_name='项目ID')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    path = models.CharField('路由路径', max_length=255, help_text='路由路径')
    title = models.CharField('路由页面标题', max_length=63, null=True, blank=True, help_text='路由页面标题')
    name = models.CharField('路由名称', max_length=63, help_text='路由名称')
    component = models.CharField('路由组件', max_length=255, null=True, blank=True, help_text='路由组件')
    redirect = models.CharField('路由重定向', max_length=255, null=True, blank=True, help_text='路由重定向')
    props = models.BooleanField('路由传参', default=False, help_text='路由传参')
    alias = models.CharField('路由别名', max_length=1023, null=True, blank=True, help_text='路由别名')
    meta = models.TextField('路由元信息', null=True, blank=True, help_text='路由元信息')
    permission = models.ForeignKey('usercenter.FuncPermission', on_delete=models.SET_NULL, null=True, default=None,
                                   related_name='+', verbose_name='路由权限')

    class Meta:
        verbose_name = '系统项目工程路由配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "SystemProjectRouter {} - {}".format(self.project, self.title)

    @property
    def permission_name(self):
        return self.permission.name if self.permission else None


# 系统项目工程菜单配置
class SystemProjectMenu(MPTTModel):
    """系统项目工程菜单配置"""
    id = TableNamePKField('SPM')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    project = models.ForeignKey('SystemProject', on_delete=models.CASCADE, related_name='menus', verbose_name='项目ID')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    name = models.CharField('名称', max_length=63, help_text='名称')
    icon = models.CharField('图标', max_length=128, null=True, blank=True, help_text='图标')
    router_name = models.CharField('路由名称', max_length=128, null=True, blank=True, help_text='路由名称')
    permission = models.ForeignKey('usercenter.FuncPermission', on_delete=models.SET_NULL, null=True, default=None,
                                   related_name='+', verbose_name='菜单权限')

    class Meta:
        verbose_name = '系统项目工程菜单配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "SystemProjectMenu {} - {}".format(self.project, self.name)


class SystemLog(models.Model):
    id = TableNamePKField('SYSLOG')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    log_level = models.IntegerField('日志级别', choices=LOG_LEVELS, default=0, help_text='日志级别')
    log_type = models.CharField('日志类别', max_length=32, db_index=True, null=True, blank=True, help_text='日志类别')
    template_id = models.CharField('模板ID', max_length=32, db_index=True, null=True, blank=True, help_text='模板ID')
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, help_text='User ID', db_constraint=False,
        related_name='+'
    )
    content = models.TextField('日志内容', null=True, blank=True, help_text='日志内容')
    user_name = models.CharField('操作用户名', max_length=64, null=True, blank=True, help_text='操作用户名')
    create_time = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = verbose_name


class SystemDataBackup(models.Model):
    id = TableNamePKField('SYSDB')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', null=True, blank=True, db_index=True)
    create_time = models.DateTimeField('操作时间', auto_now_add=True)
    user_name = models.CharField('操作用户名', max_length=64, null=True, blank=True, help_text='操作用户名')

    backup_params = models.TextField('备份参数', null=True, blank=True, help_text='备份参数')
    backup_file = models.FileField('备份文件', upload_to='system/data/backup', null=True, blank=True, help_text='备份文件')

    class Meta:
        verbose_name = '系统备份'
        verbose_name_plural = verbose_name

    def create_backup_file(self):
        from utility.sql_export import export_sys_sql
        try:
            params = json.loads(self.backup_params)
        except:
            params = {}
        default_params = {
            'include_cms': False,
            'include_data': False,
            'include_delete': False,
            'include_parameters': False,
        }
        default_params.update(params)
        default_params['sys_id'] = self.sys_id
        default_params['org_id'] = self.org_id
        logger.debug(f'SystemDataBackup default_params: {default_params}')
        sql = export_sys_sql(**default_params)
        bin_data = gzip.compress(sql.encode())
        time_stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        org_id_display = self.org_id or '0'
        self.backup_file.save(f'{self.sys_id}_{org_id_display}_{time_stamp}.sql.gz', ContentFile(bin_data))
        self.save()

    def get_sql_str(self):
        if self.backup_file:
            return gzip.decompress(self.backup_file.read()).decode()
        return None
