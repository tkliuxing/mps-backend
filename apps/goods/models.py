from utility.db_fields import TableNamePKField
from django.utils import timezone
from django.db import models


# 物品
class Goods(models.Model):
    id = TableNamePKField('G')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    name = models.CharField('名称', max_length=256, null=True, blank=True, help_text='名称')
    sn = models.CharField('编号', null=True, blank=True, max_length=256, help_text='编号')
    gps_sn = models.CharField('定位设备编号', null=True, blank=True, max_length=256, help_text='定位设备编号')
    brand = models.CharField('品牌', null=True, blank=True, max_length=256, help_text='品牌')
    size = models.CharField('规格', null=True, blank=True, max_length=256, help_text='规格')
    model_num = models.CharField('型号', null=True, blank=True, max_length=256, help_text='型号')
    status = models.CharField('状态', null=True, blank=True, max_length=128, help_text='状态')
    category = models.CharField('类别', null=True, blank=True, max_length=128, db_index=True, help_text='类别 idx')
    color = models.CharField('颜色', null=True, blank=True, max_length=32, help_text='颜色')
    material = models.CharField('材质', null=True, blank=True, max_length=128, help_text='材质')
    package = models.CharField('包装', null=True, blank=True, max_length=128, help_text='包装')
    volume = models.CharField('体积', null=True, blank=True, max_length=64, help_text='体积')
    long = models.CharField('长', null=True, blank=True, max_length=64, help_text='长')
    wide = models.CharField('宽', null=True, blank=True, max_length=64, help_text='宽')
    high = models.CharField('高', null=True, blank=True, max_length=64, help_text='高')
    quality = models.CharField('质量', null=True, blank=True, max_length=128, help_text='质量')
    number = models.CharField('数量', null=True, blank=True, max_length=32, help_text='数量')
    product_description = models.TextField('产品说明', null=True, blank=True, help_text='产品说明')
    cost_01 = models.DecimalField('成本1', max_digits=16, decimal_places=4, null=True, blank=True, help_text='成本1')
    cost_02 = models.DecimalField('成本2', max_digits=16, decimal_places=4, null=True, blank=True, help_text='成本2')
    cost_03 = models.DecimalField('成本3', max_digits=16, decimal_places=4, null=True, blank=True, help_text='成本3')
    price_01 = models.DecimalField('价格1', max_digits=16, decimal_places=4, null=True, blank=True, help_text='价格1')
    price_02 = models.DecimalField('价格2', max_digits=16, decimal_places=4, null=True, blank=True, help_text='价格2')
    price_03 = models.DecimalField('成本3', max_digits=16, decimal_places=4, null=True, blank=True, help_text='成本3')

    province = models.CharField('省', null=True, blank=True, max_length=64, db_index=True, help_text='省 idx')
    city = models.CharField('市', null=True, blank=True, max_length=64, db_index=True, help_text='城市 idx')
    region = models.CharField('区', null=True, blank=True, max_length=64, db_index=True, help_text='区域 idx')
    township = models.CharField('乡镇街道', null=True, blank=True, max_length=128, db_index=True, help_text='乡镇街道 idx')

    address = models.CharField('地址', null=True, blank=True, max_length=256, help_text='地址')
    own_org = models.ForeignKey('org.Org', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
                                verbose_name='组织机构ID')
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        help_text='用户ID', verbose_name='usercenter_user.id', db_constraint=False, db_index=True
    )
    department = models.ForeignKey('usercenter.Department', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='+', verbose_name='部门ID')
    room = models.CharField('房间', null=True, blank=True, max_length=64, help_text='房间')
    location = models.CharField('位置', null=True, blank=True, max_length=64, help_text='位置')
    validity = models.CharField('有效期', null=True, blank=True, max_length=64, help_text='有效期')
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    produced_time = models.DateField('生产日期', null=True, blank=True, help_text='生产日期')
    release_time = models.DateField('发布日期', null=True, blank=True, help_text='发布日期')
    added_time = models.DateField('上架日期', null=True, blank=True, help_text='上架日期')
    down_time = models.DateField('下架日期', null=True, blank=True, help_text='下架日期')
    import_time = models.DateField('进口日期', null=True, blank=True, help_text='进口日期')
    export_time = models.DateField('出口日期', null=True, blank=True, help_text='出口日期')
    country = models.CharField('进出口国家', null=True, blank=True, max_length=64, help_text='进出口国家')
    customs = models.CharField('海关', null=True, blank=True, max_length=64, help_text='海关')
    barcode = models.TextField('条形码', null=True, blank=True, help_text='条形码')
    qrcode = models.TextField('二维码', null=True, blank=True, help_text='二维码')
    photo = models.TextField('物品图片', null=True, blank=True, help_text='物品图片')
    longitude = models.FloatField('经度', null=True, blank=True, help_text='经度 idx')
    latitude = models.FloatField('纬度', null=True, blank=True, help_text='纬度 idx')
    altitude = models.FloatField('海拔', null=True, blank=True, help_text='海拔 idx')

    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True, help_text='父级ID必须是本表'
    )
    obj_id = models.CharField('外键字段', max_length=32, null=True, blank=True, help_text='保存人表、物表、服务表、机构表数据ID')
    template = models.ForeignKey(
        'formtemplate.FormTemplate', related_name='goods', verbose_name='模版',
        on_delete=models.SET_NULL, null=True, blank=True, db_constraint=False
    )

    field_01 = models.CharField('Field 01', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_02 = models.CharField('Field 02', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_03 = models.CharField('Field 03', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_04 = models.CharField('Field 04', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_05 = models.CharField('Field 05', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_06 = models.CharField('Field 06', max_length=1023, null=True, blank=True)
    field_07 = models.CharField('Field 07', max_length=1023, null=True, blank=True)
    field_08 = models.CharField('Field 08', max_length=1023, null=True, blank=True)
    field_09 = models.CharField('Field 09', max_length=1023, null=True, blank=True)
    field_10 = models.CharField('Field 10', max_length=1023, null=True, blank=True)

    text_01 = models.TextField('Text 01', null=True, blank=True)

    datetime_01 = models.DateTimeField('DateTime 01', null=True, blank=True, db_index=True, help_text='idx')
    datetime_02 = models.DateTimeField('DateTime 02', null=True, blank=True, db_index=True, help_text='idx')
    datetime_03 = models.DateTimeField('DateTime 03', null=True, blank=True)
    datetime_04 = models.DateTimeField('DateTime 04', null=True, blank=True)
    datetime_05 = models.DateTimeField('DateTime 05', null=True, blank=True)

    int_01 = models.BigIntegerField('Int 01', null=True, blank=True, db_index=True, help_text='idx')
    int_02 = models.BigIntegerField('Int 02', null=True, blank=True, db_index=True, help_text='idx')
    int_03 = models.BigIntegerField('Int 03', null=True, blank=True)
    int_04 = models.BigIntegerField('Int 04', null=True, blank=True)
    int_05 = models.BigIntegerField('Int 05', null=True, blank=True)

    float_01 = models.DecimalField('Float 01', max_digits=16, decimal_places=4, null=True, blank=True, db_index=True, help_text='idx')
    float_02 = models.DecimalField('Float 02', max_digits=16, decimal_places=4, null=True, blank=True, db_index=True, help_text='idx')
    float_03 = models.DecimalField('Float 03', max_digits=16, decimal_places=4, null=True, blank=True)
    float_04 = models.DecimalField('Float 04', max_digits=16, decimal_places=4, null=True, blank=True)
    float_05 = models.DecimalField('Float 05', max_digits=16, decimal_places=4, null=True, blank=True)

    class Meta:
        verbose_name = '物品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} - {}".format(self.sys_id, self.name)
