from utility.db_fields import TableNamePKField
from django.utils import timezone
from django.db import models


class Org(models.Model):
    """组织机构"""
    id = TableNamePKField('O')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    gps_sn = models.CharField('定位设备编号', null=True, blank=True, max_length=256, help_text='定位设备编号')
    name = models.CharField('名称', max_length=256, null=True, blank=True, help_text='名称')
    en_name = models.CharField('英文名', max_length=256, null=True, blank=True, help_text='英文名')
    old_name = models.CharField('曾用名', max_length=256, null=True, blank=True, help_text='曾用名')
    org_type = models.CharField('类型', max_length=128, null=True, blank=True, help_text='类型')
    org_number = models.CharField('机构代码', max_length=128, null=True, blank=True, help_text='机构代码')
    id_number = models.CharField('证照编号', max_length=128, null=True, blank=True, help_text='证照编号')
    ie_code = models.CharField('进出口代码', max_length=128, null=True, blank=True, help_text='进出口代码')
    org_status = models.CharField('状态', max_length=128, null=True, blank=True, help_text='状态')
    phone = models.CharField('联系电话', max_length=32, null=True, blank=True, help_text='联系电话')
    industry = models.CharField('行业', max_length=32, null=True, blank=True, help_text='行业')
    local = models.CharField('所属地', max_length=256, null=True, blank=True, help_text='所属地')
    address = models.CharField('地址', max_length=512, null=True, blank=True, help_text='地址')
    size = models.CharField('规模', max_length=32, null=True, blank=True, help_text='规模')
    postcode = models.CharField('邮编', max_length=32, null=True, blank=True, help_text='邮编')
    mail = models.CharField('邮箱', max_length=255, null=True, blank=True, help_text='邮箱')
    lp_name = models.CharField('法人', max_length=32, null=True, blank=True, help_text='法人')
    lp_id_type = models.CharField('法人证件类型', max_length=32, null=True, blank=True, help_text='法人证件类型')
    lp_id_number = models.CharField('法人证件号码', max_length=32, null=True, blank=True, help_text='法人证件号码')
    lp_phone = models.CharField('法人联系电话', max_length=32, null=True, blank=True, help_text='法人联系电话')
    lp_mail = models.CharField('法人邮箱', max_length=255, null=True, blank=True, help_text='法人邮箱')
    contact_name = models.CharField('联系人', max_length=32, null=True, blank=True, help_text='联系人')
    contact_phone = models.CharField('联系人联系电话', max_length=32, null=True, blank=True, help_text='联系人联系电话')
    contact_mail = models.CharField('联系人邮箱', max_length=255, null=True, blank=True, help_text='联系人邮箱')
    registered_capital = models.CharField('注册资本', max_length=32, null=True, blank=True, help_text='注册资本')
    start_date = models.DateField('成立时间', null=True, blank=True, help_text='成立时间')
    end_date = models.DateField('有效期限', null=True, blank=True, help_text='有效期限')
    business_scope = models.TextField('业务范围', null=True, blank=True, help_text='业务范围')
    start_org = models.CharField('举办单位', max_length=128, null=True, blank=True, help_text='举办单位')
    main_org = models.CharField('主管单位', max_length=128, null=True, blank=True, help_text='主管单位')
    registration_org = models.CharField('登记机关', max_length=128, null=True, blank=True, help_text='登记机关')
    registration_date = models.DateField('登记日期', null=True, blank=True, help_text='登记日期')
    link = models.CharField('网址', max_length=256, null=True, blank=True, help_text='网址')
    desc = models.TextField('简介', null=True, blank=True, help_text='简介')
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        help_text='用户ID', verbose_name='usercenter_user.id', db_constraint=False, db_index=True
    )
    department = models.ForeignKey(
        'usercenter.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', db_constraint=False
    )
    desc_article = models.ForeignKey(
        'article.Article',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='介绍',
        related_name='+',
        verbose_name='介绍',
        db_constraint=False
    )
    photo = models.TextField('公司照片', null=True, blank=True, help_text='公司照片')
    longitude = models.FloatField('经度', null=True, blank=True, help_text='经度 idx')
    latitude = models.FloatField('纬度', null=True, blank=True, help_text='纬度 idx')
    altitude = models.FloatField('海拔', null=True, blank=True, help_text='海拔 idx')
    qrcode = models.TextField('二维码', null=True, blank=True, help_text='二维码')
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)

    obj_id = models.CharField('外键字段', max_length=32, null=True, blank=True, help_text='保存人表、物表、服务表、机构表数据ID')
    template = models.ForeignKey(
        'formtemplate.FormTemplate',
        related_name='org',
        verbose_name='模版',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_constraint=False
    )

    field_01 = models.CharField('Field 01', max_length=1023, db_index=True, null=True, blank=True)
    field_02 = models.CharField('Field 02', max_length=1023, db_index=True, null=True, blank=True)
    field_03 = models.CharField('Field 03', max_length=1023, null=True, blank=True)
    field_04 = models.CharField('Field 04', max_length=1023, null=True, blank=True)
    field_05 = models.CharField('Field 05', max_length=1023, null=True, blank=True)
    field_06 = models.CharField('Field 06', max_length=1023, null=True, blank=True)
    field_07 = models.CharField('Field 07', max_length=1023, null=True, blank=True)
    field_08 = models.CharField('Field 08', max_length=1023, null=True, blank=True)
    field_09 = models.CharField('Field 09', max_length=1023, null=True, blank=True)
    field_10 = models.CharField('Field 10', max_length=1023, null=True, blank=True)
    field_11 = models.CharField('Field 11', max_length=1023, null=True, blank=True)
    field_12 = models.CharField('Field 12', max_length=1023, null=True, blank=True)
    field_13 = models.CharField('Field 13', max_length=1023, null=True, blank=True)
    field_14 = models.CharField('Field 14', max_length=1023, null=True, blank=True)
    field_15 = models.CharField('Field 15', max_length=1023, null=True, blank=True)
    field_16 = models.CharField('Field 16', max_length=1023, null=True, blank=True)
    field_17 = models.CharField('Field 17', max_length=1023, null=True, blank=True)
    field_18 = models.CharField('Field 18', max_length=1023, null=True, blank=True)
    field_19 = models.CharField('Field 19', max_length=1023, null=True, blank=True)
    field_20 = models.CharField('Field 20', max_length=1023, null=True, blank=True)
    field_21 = models.CharField('Field 21', max_length=1023, null=True, blank=True)
    field_22 = models.CharField('Field 22', max_length=1023, null=True, blank=True)
    field_23 = models.CharField('Field 23', max_length=1023, null=True, blank=True)
    field_24 = models.CharField('Field 24', max_length=1023, null=True, blank=True)
    field_25 = models.CharField('Field 25', max_length=1023, null=True, blank=True)
    field_26 = models.CharField('Field 26', max_length=1023, null=True, blank=True)
    field_27 = models.CharField('Field 27', max_length=1023, null=True, blank=True)
    field_28 = models.CharField('Field 28', max_length=1023, null=True, blank=True)
    field_29 = models.CharField('Field 29', max_length=1023, null=True, blank=True)
    field_30 = models.CharField('Field 30', max_length=1023, null=True, blank=True)
    field_31 = models.CharField('Field 31', max_length=1023, null=True, blank=True)
    field_32 = models.CharField('Field 32', max_length=1023, null=True, blank=True)
    field_33 = models.CharField('Field 33', max_length=1023, null=True, blank=True)
    field_34 = models.CharField('Field 34', max_length=1023, null=True, blank=True)
    field_35 = models.CharField('Field 35', max_length=1023, null=True, blank=True)
    field_36 = models.CharField('Field 36', max_length=1023, null=True, blank=True)
    field_37 = models.CharField('Field 37', max_length=1023, null=True, blank=True)
    field_38 = models.CharField('Field 38', max_length=1023, null=True, blank=True)
    field_39 = models.CharField('Field 39', max_length=1023, null=True, blank=True)
    field_40 = models.CharField('Field 40', max_length=1023, null=True, blank=True)
    field_41 = models.CharField('Field 41', max_length=1023, null=True, blank=True)
    field_42 = models.CharField('Field 42', max_length=1023, null=True, blank=True)
    field_43 = models.CharField('Field 43', max_length=1023, null=True, blank=True)
    field_44 = models.CharField('Field 44', max_length=1023, null=True, blank=True)
    field_45 = models.CharField('Field 45', max_length=1023, null=True, blank=True)
    field_46 = models.CharField('Field 46', max_length=1023, null=True, blank=True)
    field_47 = models.CharField('Field 47', max_length=1023, null=True, blank=True)
    field_48 = models.CharField('Field 48', max_length=1023, null=True, blank=True)
    field_49 = models.CharField('Field 49', max_length=1023, null=True, blank=True)
    field_50 = models.CharField('Field 50', max_length=1023, null=True, blank=True)

    field_01_display = models.TextField('Field 01 display', null=True, blank=True)
    field_02_display = models.TextField('Field 02 display', null=True, blank=True)
    field_03_display = models.TextField('Field 03 display', null=True, blank=True)
    field_04_display = models.TextField('Field 04 display', null=True, blank=True)
    field_05_display = models.TextField('Field 05 display', null=True, blank=True)
    field_06_display = models.TextField('Field 06 display', null=True, blank=True)
    field_07_display = models.TextField('Field 07 display', null=True, blank=True)
    field_08_display = models.TextField('Field 08 display', null=True, blank=True)
    field_09_display = models.TextField('Field 09 display', null=True, blank=True)
    field_10_display = models.TextField('Field 10 display', null=True, blank=True)

    text_01 = models.TextField('Text_01', null=True, blank=True)
    text_02 = models.TextField('Text_02', null=True, blank=True)
    text_03 = models.TextField('Text_03', null=True, blank=True)
    text_04 = models.TextField('Text_04', null=True, blank=True)
    text_05 = models.TextField('Text_05', null=True, blank=True)

    class Meta:
        verbose_name = '01.组织机构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} - {}".format(self.sys_id, self.name)
