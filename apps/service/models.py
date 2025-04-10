from utility.db_fields import TableNamePKField

from django.utils import timezone
from django.db import models


# 服务
class Services(models.Model):
    id = TableNamePKField('S')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)

    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        help_text='用户ID', verbose_name='usercenter_user.id', db_constraint=False, db_index=True
    )
    department = models.ForeignKey(
        'usercenter.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', db_constraint=False
    )
    customera = models.ForeignKey('customer.Customer', null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='+', verbose_name='甲方ID customera_id to customer_customer',
                                  db_constraint=False)
    customerb = models.ForeignKey('customer.Customer', null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='+', verbose_name='乙方ID customerb_id to customer_customer',
                                  db_constraint=False)
    customerc = models.ForeignKey('customer.Customer', null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name='+', verbose_name='丙方ID customerc_id to customer_customer',
                                  db_constraint=False)

    usera = models.ForeignKey('usercenter.User', null=True, blank=True, on_delete=models.SET_NULL,
                              related_name='+', verbose_name='甲方ID usera_id to usercenter_user', db_constraint=False)
    userb = models.ForeignKey('usercenter.User', null=True, blank=True, on_delete=models.SET_NULL,
                              related_name='+', verbose_name='乙方ID userb_id to usercenter_user', db_constraint=False)
    userc = models.ForeignKey('usercenter.User', null=True, blank=True, on_delete=models.SET_NULL,
                              related_name='+', verbose_name='丙方ID userc_id to usercenter_user', db_constraint=False)

    customera_name = models.CharField('甲方名称', max_length=256, null=True, blank=True, help_text='甲方名称')
    customerb_name = models.CharField('乙方名称', max_length=256, null=True, blank=True, help_text='乙方名称')
    customerc_name = models.CharField('丙方名称', max_length=256, null=True, blank=True, help_text='丙方名称')

    orga = models.ForeignKey('org.Org', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
                             verbose_name='甲方组织机构ID orga_id to org_org', db_constraint=False)
    orgb = models.ForeignKey('org.Org', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
                             verbose_name='乙方组织机构ID orgb_id to org_org', db_constraint=False)
    orgc = models.ForeignKey('org.Org', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
                             verbose_name='丙方组织机构ID orgc_id to org_org', db_constraint=False)

    orga_name = models.CharField('甲方组织机构名称', max_length=256, null=True, blank=True, help_text='甲方组织机构名称')
    orgb_name = models.CharField('乙方组织机构名称', max_length=256, null=True, blank=True, help_text='乙方组织机构名称')
    orgc_name = models.CharField('丙方组织机构名称', max_length=256, null=True, blank=True, help_text='丙方组织机构名称')

    a_persion = models.CharField('甲方联系人', max_length=512, null=True, blank=True, help_text='甲方联系人')
    b_persion = models.CharField('乙方联系人', max_length=512, null=True, blank=True, help_text='乙方联系人')
    c_persion = models.CharField('丙方联系人', max_length=512, null=True, blank=True, help_text='丙方联系人')

    a_phone = models.CharField('甲方联系电话', max_length=512, null=True, blank=True, help_text='甲方联系电话')
    b_phone = models.CharField('乙方联系电话', max_length=512, null=True, blank=True, help_text='乙方联系电话')
    c_phone = models.CharField('丙方联系电话', max_length=512, null=True, blank=True, help_text='丙方联系电话')

    contract_sn = models.CharField('合同编号', null=True, blank=True, max_length=256, help_text='合同编号', db_index=True)
    contract_price = models.DecimalField('合同价格', max_digits=16, decimal_places=4, null=True, blank=True, help_text='合同价格')
    sign_time = models.DateField('签订时间', null=True, blank=True, help_text='签订时间')
    sign_addr = models.CharField('签订地点', null=True, blank=True, max_length=256, help_text='签订地点')
    name = models.CharField('服务名称', max_length=256, null=True, blank=True, help_text='服务名称')
    sn = models.CharField('服务编号', null=True, blank=True, max_length=256, help_text='服务编号', db_index=True)
    price = models.DecimalField('限定价格', max_digits=16, decimal_places=4, null=True, blank=True, help_text='限定价格')
    desc = models.TextField('服务内容', null=True, blank=True, help_text='服务内容')
    deadline = models.CharField('服务期限', null=True, blank=True, max_length=32, help_text='服务期限')
    start_time = models.DateField('服务开始日期', null=True, blank=True, help_text='服务开始日期')
    end_time = models.DateField('服务结束日期', null=True, blank=True, help_text='服务结束日期')

    bidding_company = models.CharField('招标单位', max_length=256, null=True, blank=True, help_text='招标单位名称或ID')
    bidding_time = models.DateTimeField('招标时间', null=True, blank=True, help_text='招标时间')

    check_time = models.DateTimeField('验收时间', null=True, blank=True, help_text='验收时间')
    check_price = models.DecimalField('验收金额', max_digits=16, decimal_places=4, null=True, blank=True, help_text='验收金额')

    audit_time = models.DateTimeField('审计时间', null=True, blank=True, help_text='审计时间')
    audit1_price = models.DecimalField('报审金额', max_digits=16, decimal_places=4, null=True, blank=True, help_text='报审金额')
    audit2_price = models.DecimalField('初审金额', max_digits=16, decimal_places=4, null=True, blank=True, help_text='初审金额')
    audit3_price = models.DecimalField('终审金额', max_digits=16, decimal_places=4, null=True, blank=True, help_text='终审金额')

    audit_status = models.CharField('审计或验收阶段状态', max_length=64, null=True, blank=True, help_text='审计或验收阶段状态')
    design_status = models.CharField('设计阶段状态', max_length=64, null=True, blank=True, help_text='设计阶段状态')
    construction_status = models.CharField('施工阶段状态', max_length=64, null=True, blank=True, help_text='施工阶段状态')

    file = models.TextField('附件', null=True, blank=True, help_text='附件')
    article = models.ForeignKey(
        'article.Article', on_delete=models.SET_NULL, null=True, blank=True,
        help_text='介绍 article_id to article_article',
        related_name='+', verbose_name='内容链接', db_constraint=False
    )
    create_user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='创建人', help_text='创建人 create_user_id to usercenter_user', db_constraint=False
    )
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    longitude = models.FloatField('经度', null=True, blank=True, help_text='经度 idx')
    latitude = models.FloatField('纬度', null=True, blank=True, help_text='纬度 idx')
    altitude = models.FloatField('海拔', null=True, blank=True, help_text='海拔 idx')

    obj_id = models.CharField('外键字段', max_length=32, null=True, blank=True, help_text='保存人表、物表、服务表、机构表数据ID')
    template = models.ForeignKey(
        'formtemplate.FormTemplate', related_name='services', verbose_name='模版',
        on_delete=models.SET_NULL, null=True, blank=True,
        help_text='template_id to formtemplate_formtemplate', db_constraint=False
    )

    field_01 = models.CharField('Field 01', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_02 = models.CharField('Field 02', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_03 = models.CharField('Field 03', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_04 = models.CharField('Field 04', max_length=1023, null=True, blank=True)
    field_05 = models.CharField('Field 05', max_length=1023, null=True, blank=True)
    field_06 = models.CharField('Field 06', max_length=1023, null=True, blank=True)
    field_07 = models.CharField('Field 07', max_length=1023, null=True, blank=True)
    field_08 = models.CharField('Field 08', max_length=1023, null=True, blank=True)
    field_09 = models.CharField('Field 09', max_length=1023, null=True, blank=True)
    field_10 = models.CharField('Field 10', max_length=1023, null=True, blank=True)

    text_01 = models.TextField('Text 01', null=True, blank=True)

    date_01 = models.DateField('Date 01', null=True, blank=True)
    date_02 = models.DateField('Date 02', null=True, blank=True)
    date_03 = models.DateField('Date 03', null=True, blank=True)
    date_04 = models.DateField('Date 04', null=True, blank=True)
    date_05 = models.DateField('Date 05', null=True, blank=True)

    datetime_01 = models.DateTimeField('Datetime 01', null=True, blank=True)
    datetime_02 = models.DateTimeField('Datetime 02', null=True, blank=True)
    datetime_03 = models.DateTimeField('Datetime 03', null=True, blank=True)
    datetime_04 = models.DateTimeField('Datetime 04', null=True, blank=True)
    datetime_05 = models.DateTimeField('Datetime 05', null=True, blank=True)

    int_01 = models.BigIntegerField('Int 01', null=True, blank=True, db_index=True, help_text='idx')
    int_02 = models.BigIntegerField('Int 02', null=True, blank=True, db_index=True, help_text='idx')
    int_03 = models.BigIntegerField('Int 03', null=True, blank=True)
    int_04 = models.BigIntegerField('Int 04', null=True, blank=True)
    int_05 = models.BigIntegerField('Int 05', null=True, blank=True)
    int_06 = models.BigIntegerField('Int 06', null=True, blank=True)
    int_07 = models.BigIntegerField('Int 07', null=True, blank=True)
    int_08 = models.BigIntegerField('Int 08', null=True, blank=True)
    int_09 = models.BigIntegerField('Int 09', null=True, blank=True)
    int_10 = models.BigIntegerField('Int 10', null=True, blank=True)

    float_01 = models.DecimalField('Float 01', max_digits=16, decimal_places=4, null=True, blank=True, db_index=True,
                                   help_text='idx')
    float_02 = models.DecimalField('Float 02', max_digits=16, decimal_places=4, null=True, blank=True, db_index=True,
                                   help_text='idx')
    float_03 = models.DecimalField('Float 03', max_digits=16, decimal_places=4, null=True, blank=True)
    float_04 = models.DecimalField('Float 04', max_digits=16, decimal_places=4, null=True, blank=True)
    float_05 = models.DecimalField('Float 05', max_digits=16, decimal_places=4, null=True, blank=True)
    float_06 = models.DecimalField('Float 06', max_digits=16, decimal_places=4, null=True, blank=True)
    float_07 = models.DecimalField('Float 07', max_digits=16, decimal_places=4, null=True, blank=True)
    float_08 = models.DecimalField('Float 08', max_digits=16, decimal_places=4, null=True, blank=True)
    float_09 = models.DecimalField('Float 09', max_digits=16, decimal_places=4, null=True, blank=True)
    float_10 = models.DecimalField('Float 10', max_digits=16, decimal_places=4, null=True, blank=True)

    class Meta:
        verbose_name = '服务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} - {}".format(self.sys_id, self.name)
