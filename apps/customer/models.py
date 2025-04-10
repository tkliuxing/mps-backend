import datetime

from django.utils import timezone

from utility.db_fields import TableNamePKField
from django.db import models


class Customer(models.Model):
    """人员"""
    id = TableNamePKField('C')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    sn = models.CharField('编号', null=True, blank=True, db_index=True, max_length=256, help_text='编号')
    gps_sn = models.CharField('定位设备编号', null=True, blank=True, max_length=256, help_text='定位设备编号')
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, db_constraint=False, help_text='用户ID'
    )
    name = models.CharField('姓名', max_length=32, null=True, blank=True, help_text='姓名')
    en_name = models.CharField('英文名', max_length=64, null=True, blank=True, help_text='英文名')
    old_name = models.CharField('曾用名', max_length=64, null=True, blank=True, help_text='曾用名')
    nick_name = models.CharField('昵称', max_length=31, null=True, blank=True, help_text='昵称')
    gender = models.CharField('性别', max_length=2, null=True, blank=True, help_text='性别')
    country = models.CharField('国籍', max_length=64, null=True, blank=True, help_text='国籍')
    nation = models.CharField('民族', max_length=64, null=True, blank=True, help_text='民族')
    political_status = models.CharField('政治面貌', max_length=64, null=True, blank=True, help_text='政治面貌')
    certificate_type = models.CharField('证件类型', max_length=64, null=True, blank=True, help_text='证件类型')
    certificate_number = models.CharField('证件号码', max_length=64, null=True, blank=True, help_text='证件号码')
    birthday = models.DateField('出生日期', null=True, blank=True, help_text='出生日期')
    death_date = models.DateField('死亡日期', null=True, blank=True, help_text='死亡日期')
    birthplace = models.CharField('出生地', max_length=256, null=True, blank=True, help_text='出生地')
    hometown = models.CharField('籍贯', max_length=256, null=True, blank=True, help_text='籍贯')
    address = models.TextField('住址', null=True, blank=True, help_text='住址')
    mail = models.CharField('邮箱', max_length=255, null=True, blank=True, help_text='邮箱')
    qq = models.CharField('QQ', max_length=32, null=True, blank=True, help_text='QQ')
    phone_01 = models.CharField('联系电话1', max_length=32, null=True, blank=True, help_text='联系电话1')
    phone_02 = models.CharField('联系电话2', max_length=32, null=True, blank=True, help_text='联系电话2')
    emergency_contact = models.CharField('紧急联系人', max_length=32, null=True, blank=True, help_text='紧急联系人')
    emergency_phone = models.CharField('紧急联系电话', max_length=32, null=True, blank=True, help_text='紧急联系电话')
    issuing_authority = models.CharField('发证机关', max_length=64, null=True, blank=True, help_text='发证机关')
    effective_start_date = models.DateField('有效开始日期', null=True, blank=True, help_text='有效开始日期')
    effective_end_date = models.DateField('有效结束日期', null=True, blank=True, help_text='有效结束日期')
    graduated_college = models.CharField('毕业院校', max_length=256, null=True, blank=True, help_text='毕业院校')
    enrollment_date = models.DateField('入学日期', null=True, blank=True, help_text='入学日期')
    graduation_date = models.DateField('毕业日期', null=True, blank=True, help_text='毕业日期')
    education = models.CharField('学历', max_length=256, null=True, blank=True, help_text='学历')
    academic_degree = models.CharField('学位', max_length=256, null=True, blank=True, help_text='学位')
    majors = models.CharField('专业', max_length=256, null=True, blank=True, help_text='专业')
    class_name = models.CharField('班级', max_length=256, null=True, blank=True, help_text='班级')
    profession = models.CharField('职业', max_length=256, null=True, blank=True, help_text='职业')
    qualification_name = models.CharField('资格证书', max_length=256, null=True, blank=True, help_text='资格证书')
    qualification_number = models.CharField('资格证书编号', max_length=256, null=True, blank=True, help_text='资格证书编号')
    qualification_level = models.CharField('资格证书等级', max_length=256, null=True, blank=True, help_text='资格证书等级')
    qualification_source = models.CharField('资格证书发证机构', max_length=256, null=True, blank=True, help_text='资格证书发证机构')
    work_place = models.CharField('工作单位', max_length=255, null=True, blank=True, help_text='工作单位')
    inauguration_date = models.DateField('入职时间', null=True, blank=True, help_text='入职时间')
    department = models.ForeignKey(
        'usercenter.Department', on_delete=models.SET_NULL, null=True, blank=True,
        help_text='部门ID department_id to usercenter_department',
        related_name='+', verbose_name='部门'
    )
    job_position = models.CharField('职位', max_length=32, null=True, blank=True, help_text='职位')
    job_post = models.CharField('岗位', max_length=32, null=True, blank=True, help_text='岗位')
    job_content = models.TextField('工作内容', null=True, blank=True, help_text='工作内容')
    id_photo = models.TextField('证件照片', null=True, blank=True, help_text='证件照片')
    photo = models.TextField('本人照片', null=True, blank=True, help_text='本人照片')
    qrcode = models.TextField('二维码', null=True, blank=True, help_text='二维码')

    marital_status = models.CharField(
        '婚姻状况', max_length=32, default='未知', help_text='婚姻状况', null=True, blank=True
    )
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    end_date = models.DateField('有效期截止日', null=True, blank=True, help_text='有效期截止日')
    remark = models.TextField('备注', null=True, blank=True, help_text='备注')
    longitude = models.FloatField('经度', null=True, blank=True, help_text='经度 idx')
    latitude = models.FloatField('纬度', null=True, blank=True, help_text='纬度 idx')
    altitude = models.FloatField('海拔', null=True, blank=True, help_text='海拔 idx')

    obj_id = models.CharField('外键字段', max_length=32, null=True, blank=True, help_text='保存人表、物表、服务表、机构表数据ID')
    template = models.ForeignKey(
        'formtemplate.FormTemplate', related_name='customer', verbose_name='模版',
        on_delete=models.SET_NULL, null=True, blank=True, db_constraint=False,
        help_text='模版ID formtemplate_id to formtemplate_formtemplate',
    )

    field_01 = models.CharField('Field 01', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_02 = models.CharField('Field 02', max_length=1023, null=True, blank=True, db_index=True, help_text='idx')
    field_03 = models.CharField('Field 03', max_length=1023, null=True, blank=True)
    field_04 = models.CharField('Field 04', max_length=1023, null=True, blank=True)
    field_05 = models.CharField('Field 05', max_length=1023, null=True, blank=True)
    field_06 = models.CharField('Field 06', max_length=1023, null=True, blank=True)
    field_07 = models.CharField('Field 07', max_length=1023, null=True, blank=True)
    field_08 = models.CharField('Field 08', max_length=1023, null=True, blank=True)
    field_09 = models.CharField('Field 09', max_length=1023, null=True, blank=True)
    field_10 = models.CharField('Field 10', max_length=1023, null=True, blank=True)

    datetime_01 = models.DateTimeField('DateTime 01', null=True, blank=True, db_index=True, help_text='idx')
    datetime_02 = models.DateTimeField('DateTime 02', null=True, blank=True, db_index=True, help_text='idx')

    int_01 = models.BigIntegerField('Int 01', null=True, blank=True, db_index=True, help_text='idx')
    int_02 = models.BigIntegerField('Int 02', null=True, blank=True, db_index=True, help_text='idx')
    int_03 = models.BigIntegerField('Int 03', null=True, blank=True)
    int_04 = models.BigIntegerField('Int 04', null=True, blank=True)
    int_05 = models.BigIntegerField('Int 05', null=True, blank=True)

    text_01 = models.TextField('Text 01', null=True, blank=True)
    json_01 = models.TextField('JSON 01', null=True, blank=True)

    class Meta:
        verbose_name = '01.人员'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} {}".format(self.pk, self.name)
