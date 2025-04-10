import datetime
from decimal import Decimal

from django.db import models
from django.utils import timezone

from utility.db_fields import TableNamePKField


# 账户表
class Account(models.Model):
    """账户表"""
    id = TableNamePKField('ACC')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True, help_text='用户ID', db_constraint=False
    )
    obj_id = models.CharField('所属对象ID', max_length=64, db_index=True, null=True, blank=True, help_text='所属对象ID')
    acc_1_name = models.CharField('账户1名称', max_length=64, null=True, blank=True, help_text='账户1名称')
    acc_1_type = models.CharField('账户1类型', max_length=64, null=True, blank=True, help_text='账户1类型')
    acc_1_balance = models.DecimalField(
        '账户1余额', max_digits=14, decimal_places=3, default=Decimal('0'), null=True, blank=True, help_text='账户1余额'
    )
    acc_1_lock = models.DecimalField(
        '账户1锁定', max_digits=14, decimal_places=3, default=Decimal('0'), null=True, blank=True, help_text='账户1锁定'
    )
    acc_2_name = models.CharField('账户2名称', max_length=64, null=True, blank=True, help_text='账户2名称')
    acc_2_type = models.CharField('账户2类型', max_length=64, null=True, blank=True, help_text='账户2类型')
    acc_2_balance = models.DecimalField(
        '账户2余额', max_digits=14, decimal_places=3, default=Decimal('0'), null=True, blank=True, help_text='账户2余额'
    )
    acc_2_lock = models.DecimalField(
        '账户2锁定', max_digits=14, decimal_places=3, default=Decimal('0'), null=True, blank=True, help_text='账户2锁定'
    )
    acc_3_name = models.CharField('账户3名称', max_length=64, null=True, blank=True, help_text='账户3名称')
    acc_3_type = models.CharField('账户3类型', max_length=64, null=True, blank=True, help_text='账户3类型')
    acc_3_balance = models.DecimalField(
        '账户3余额', max_digits=14, decimal_places=3, default=Decimal('0'), null=True, blank=True, help_text='账户3余额'
    )
    acc_3_lock = models.DecimalField(
        '账户3锁定', max_digits=14, decimal_places=3, default=Decimal('0'), null=True, blank=True, help_text='账户3锁定'
    )
    jifen_acc = models.CharField('积分账户名称', max_length=64, null=True, blank=True, help_text='积分账户名称')
    jifen_balance = models.DecimalField(
        '积分余额', max_digits=14, decimal_places=3, default=Decimal('0'), null=True, blank=True, help_text='积分余额'
    )
    create_time = models.DateTimeField(default=timezone.now, db_index=True, help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, help_text='更新时间')

    class Meta:
        verbose_name = '账户表'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return f'账户表: {self.id}'


# 账户明细
class AccountStatements(models.Model):
    INCOMIE = '收入'
    EXPENDITURE = '支出'
    LOCK = '锁定'
    PAYMENT = '支付'

    id = TableNamePKField('ACCS')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    acc = models.ForeignKey(
        'Account', on_delete=models.CASCADE, db_constraint=False, related_name='statements',
        help_text='账户ID'
    )
    acc_name = models.CharField('账户N名称', max_length=64, null=True, blank=True, help_text='账户N名称')
    record_type = models.CharField('记录类型', max_length=16)
    amount = models.DecimalField(
        '金额', max_digits=14, decimal_places=3, help_text='金额'
    )
    used_amount = models.DecimalField(
        '已用金额', max_digits=14, decimal_places=3, default=Decimal('0'), help_text='已用金额'
    )
    end_time = models.DateTimeField('到期时间', null=True, blank=True, help_text='到期时间')
    order_num = models.CharField('订单号', max_length=64, null=True, blank=True, help_text='订单号')

    tpp_name = models.CharField('第三方支付名称', max_length=16, null=True, blank=True, help_text='第三方支付名称')
    tpp_no = models.CharField('第三方支付流水号', max_length=64, null=True, blank=True, help_text='第三方支付流水号')
    tpp_desc = models.TextField('第三方支付其他信息', null=True, blank=True, help_text='第三方支付其他信息')

    desc = models.TextField('说明', null=True, blank=True, help_text='说明')
    create_time = models.DateTimeField(auto_now_add=True, help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, help_text='更新时间')

    field_01 = models.CharField('备用字段01', max_length=64, null=True, blank=True, help_text='备用字段01')
    field_02 = models.CharField('备用字段02', max_length=64, null=True, blank=True, help_text='备用字段02')
    field_03 = models.CharField('备用字段03', max_length=64, null=True, blank=True, help_text='备用字段03')
    field_04 = models.CharField('备用字段04', max_length=64, null=True, blank=True, help_text='备用字段04')
    field_05 = models.CharField('备用字段05', max_length=64, null=True, blank=True, help_text='备用字段05')

    float_01 = models.DecimalField('备用浮点01', max_digits=14, decimal_places=3, null=True, blank=True, help_text='备用浮点01')
    float_02 = models.DecimalField('备用浮点02', max_digits=14, decimal_places=3, null=True, blank=True, help_text='备用浮点02')
    float_03 = models.DecimalField('备用浮点03', max_digits=14, decimal_places=3, null=True, blank=True, help_text='备用浮点03')
    float_04 = models.DecimalField('备用浮点04', max_digits=14, decimal_places=3, null=True, blank=True, help_text='备用浮点04')
    float_05 = models.DecimalField('备用浮点05', max_digits=14, decimal_places=3, null=True, blank=True, help_text='备用浮点05')

    class Meta:
        verbose_name = '账户明细表'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return f'账户明细表: {self.id} {self.id}'

    @property
    def is_end(self):
        if self.end_time and self.end_time < datetime.datetime.now():
            return True
        return False
