import json
import types
import org
import customer.models
import org.models
import service.models
import goods.models
from typing import Optional, Dict, Type, List, Any, Union
from django.utils import timezone
from django.db import models
from django.core.cache import cache
from utility.db_fields import TableNamePKField
from .const import M2M_MODELS_CHOICES


TemplateModelType = \
    Type['FormData'] | \
    Type['org.models.Org'] | \
    Type['service.models.Services'] | \
    Type['customer.models.Customer'] | \
    Type['goods.models.Goods']


def get_template_field_rel_cache_key(template_id: str) -> str:
    return f'{template_id}-FF'


# 模版字段
class FormFields(models.Model):
    """模版字段"""
    id = TableNamePKField('FF')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    template = models.ForeignKey(
        'FormTemplate', related_name='fields', verbose_name='模版', on_delete=models.CASCADE)
    col_title = models.CharField('字段含义', max_length=256, help_text='字段含义')
    alias = models.CharField('别名', max_length=256, default='', blank=True, help_text='别名')
    col_name = models.CharField('数据库字段名', max_length=255, help_text='数据库字段名')
    in_filter = models.BooleanField('可过滤', default=False, help_text='可过滤')
    is_required = models.BooleanField('必填项', default=True, null=True, blank=True, help_text='必填项')
    widget = models.CharField('控件类型', max_length=16, help_text='控件类型')
    widget_attr = models.CharField('控件属性', max_length=255, help_text='控件属性')
    verify_exp = models.CharField('校验表达式', max_length=255, help_text='校验表达式')
    related_template = models.ForeignKey(
        'FormTemplate', related_name='+', verbose_name='数据ID关联模版',
        on_delete=models.SET_NULL, null=True, blank=True, help_text='数据ID关联模版'
    )
    local_data_source = models.TextField('字段内数据定义', null=True, blank=True, help_text='字段内数据定义，每行一个选项')
    sort_num = models.PositiveIntegerField('序号', default=1, help_text='序号')
    data = models.TextField('Data', null=True, blank=True, help_text='Data')
    is_related = models.BooleanField(default=False, help_text='是否是外键字段(obj_id)关联显示内容')
    desc = models.CharField('字段说明', max_length=255, null=True, blank=True, help_text='字段说明')
    is_vant_show = models.BooleanField('手机端查看项', default=False, help_text='手机端查看项')
    unique = models.BooleanField('和org_id联合唯一', default=False, help_text='和org_id联合唯一')

    is_m2m = models.BooleanField('多对多关联', default=False, help_text='多对多关联')
    m2m_model = models.CharField('多对多关联模型', max_length=255, choices=M2M_MODELS_CHOICES, null=True, blank=True, help_text='多对多关联模型')

    class Meta:
        verbose_name = '02.模板字段'
        verbose_name_plural = verbose_name

    @property
    def field_alias(self) -> str:
        """字段最终别名，可能是别名或原始数据库字段名"""
        return self.alias or self.col_name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        cache.set(self.pk, self)
        tmpl_key = get_template_field_rel_cache_key(str(self.template_id))
        tmpl_fld_list = cache.get(tmpl_key)
        if tmpl_fld_list is None:
            cache.set(tmpl_key, [self.pk])
        elif self.pk not in tmpl_fld_list:
            tmpl_fld_list.append(self.pk)
            cache.set(tmpl_key, tmpl_fld_list)

    def delete(self, using=None, keep_parents=False):
        pk = str(self.pk)
        template_id = str(self.template_id)  # type: ignore
        result = super().delete(using, keep_parents)
        cache.delete(pk)
        tmpl_key = get_template_field_rel_cache_key(template_id)
        tmpl_fld_list = cache.get(tmpl_key)  # type: list
        if tmpl_fld_list is None:
            return result
        elif pk in tmpl_fld_list:
            tmpl_fld_list.remove(pk)
            cache.set(tmpl_key, tmpl_fld_list)
        return result

    @property
    def data_source(self) -> Dict[str, Any]:
        """字段内数据定义"""
        if self.local_data_source:
            return json.loads(self.local_data_source)
        return {}


# 模板
class FormTemplate(models.Model):
    """模板"""
    FORM_TYPE = (
        (1, '单行表单'),
        (2, '多行表单'),
        (3, '富文本'),
    )
    id = TableNamePKField('FT')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    fenlei = models.CharField('分类ID', max_length=64, db_index=True, null=True, blank=True, help_text='分类ID')
    api_version = models.CharField('接口版本', max_length=128, blank=True, default='v1', help_text='接口版本')
    api_name = models.CharField('接口名称', max_length=128, blank=True, default='formdata', help_text='接口名称(去掉/api/v1/和末尾/)')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True, help_text='父级模板'
    )
    from_template = models.ForeignKey(
        'self', related_name='+', on_delete=models.SET_NULL, null=True, blank=True, help_text='复制自模板', db_constraint=False
    )
    title = models.CharField('模板标题', max_length=127, help_text='模板标题')
    form_type = models.IntegerField('表单类型', choices=FORM_TYPE, default=1)
    sort_num = models.PositiveIntegerField('序号', default=1, help_text='序号')
    keyword = models.CharField('关键字', max_length=255, null=True, blank=True, db_index=True, help_text='关键字')
    remark = models.CharField('备注', max_length=1023, null=True, blank=True, help_text='备注')

    department = models.ManyToManyField(
        'usercenter.Department', blank=True, related_name='+',
        help_text='部门ID数组', verbose_name='usercenter_department.id'
    )

    table_lines = models.TextField('多行表单行头', null=True, blank=True, help_text='多行表单行头(用JSON字符串存储)')
    header_conf = models.TextField('导入导出表头定义', null=True, blank=True, help_text='导入导出表头定义(用JSON字符串存储)')

    code = models.TextField('代码', null=True, blank=True, help_text='代码')
    photo = models.TextField('截图', null=True, blank=True, help_text='截图')
    need_login = models.BooleanField('需登陆', default=False, help_text='需登陆')

    permission = models.ForeignKey(
        'usercenter.FuncPermission', on_delete=models.SET_NULL, null=True, blank=True, help_text='功能模块',
        db_constraint=False, db_index=True
    )
    creator = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, help_text='创建人'
    )

    class Meta:
        verbose_name = '01.模板'
        verbose_name_plural = verbose_name
        ordering = ['sort_num']

    def __str__(self):
        return self.title

    @property
    def api_path(self):
        return "/api/{}/{}/".format(self.api_version, self.api_name)

    @property
    def create_time_display(self):
        return self.create_time.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def field_names(self):
        """该模版的所有非关联字段的数据库字段名"""
        return [x.col_name for x in self.no_related_fields]

    @property
    def all_alias_names(self):
        """该模版的所有字段别名"""
        return [x.field_alias for x in self.all_fields]

    @property
    def all_fields(self) -> List[FormFields]:
        """属于该模版的所有字段"""
        if not hasattr(self, '_field_cache'):
            self._field_cache = sorted(self.fields.all(), key=lambda x: x.sort_num)
        return self._field_cache

    @property
    def related_fields(self) -> List[FormFields]:
        return [f for f in self.all_fields if f.is_related]

    @property
    def no_related_fields(self) -> List[FormFields]:
        """该模版的所有非关联字段"""
        return [f for f in self.all_fields if not f.is_related]

    @property
    def filter_fields(self) -> List[FormFields]:
        """该模版的所有查询字段字段"""
        return list(filter(lambda x: x.in_filter, self.all_fields))

    @property
    def obj_id_field(self) -> Optional[FormFields]:
        """该模版的关联ID字段"""
        obj_id_fields = [f for f in self.all_fields if f.col_name == 'obj_id' and f.related_template]
        if obj_id_fields:
            return obj_id_fields[0]

    @property
    def unique_fields(self) -> List[FormFields]:
        """该模版的所有唯一约束字段"""
        return list(filter(lambda x: x.unique, self.all_fields))

    @property
    def has_rel_template(self) -> bool:
        """该模版是否有关联模版"""
        return bool(self.obj_id_field and self.obj_id_field.related_template and self.related_fields)

    @property
    def rel_model(self):
        if self.has_rel_template and self.obj_id_field and self.obj_id_field.related_template:
            return self.obj_id_field.related_template.get_model()
        return None

    def get_annotate_dict(self) -> Dict[str, models.F]:
        """返回用于对本模版模型的annotate查询的参数"""
        annotate_dict = {}
        for ff in self.related_fields:
            annotate_dict[ff.field_alias] = models.F(f'obj__{ff.col_name}')
        return annotate_dict

    def get_related_model(self) -> Type[models.Model]:
        """返回本模版的代理模型"""
        if not self.has_rel_template:
            return self.get_model()
        if not self.obj_id_field or not self.obj_id_field.related_template:
            return self.get_model()
        rel_template = self.obj_id_field.related_template
        rel_model_class = rel_template.get_model()
        model_class = self.get_model()
        app_label_name = model_class._meta.app_label
        # 如果有关联字段，则创建一个带有关联字段外键的代理模型用于关系取值
        # TODO: 考虑有多个关联ID字段的情况下如何增加多个外键到代理模型中（元类或type）
        # Example:
        # meta = type('Meta', (), {'proxy':True, 'app_label':'service'})
        # type('NewService', (Services,), {'Meta':meta, '__module__':model_class.__module__})
        if self.related_fields and issubclass(model_class, models.Model):
            class RelData(model_class):  # type: ignore
                obj = models.ForeignKey(
                    rel_model_class, on_delete=models.DO_NOTHING, null=True, blank=True, db_constraint=False,
                    related_name='+', db_column='obj_id'
                )

                class Meta:
                    proxy = True
                    app_label = app_label_name
            return RelData
        return model_class

    def get_model(self) -> TemplateModelType:
        """返回当前模版对应的Model类"""
        from service.models import Services
        from org.models import Org
        from customer.models import Customer
        from goods.models import Goods
        model_list = [Services, Org, Customer, Goods, FormData]
        model_api_name_dict = dict(
            map(lambda x: (x._meta.model_name, x), model_list)
        )
        this_model = model_api_name_dict.get(self.api_name)
        if this_model is None:
            raise ValueError(
                'api_name not in [services, customer, goods, formdata, org]! "{}"'.format(self.api_name))
        return this_model

    def get_serializer_class(self):
        """返回当前模版对应的Serializer类"""
        from .api import get_serializer_class
        return get_serializer_class(self.get_model(), self)

    @property
    def model_table_name(self) -> str:
        """该模版的数据表名"""
        model_class = self.get_model()
        return model_class._meta.db_table

    @classmethod
    def get_by_id(cls, template_id: str) -> 'FormTemplate':
        return cls.objects.prefetch_related('fields').get(pk=template_id)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        cache.set(self.pk, self)

    def delete(self, using=None, keep_parents=False):
        pk = str(self.pk)
        result = super().delete(using, keep_parents)
        cache.delete(pk)
        tmpl_key = get_template_field_rel_cache_key(pk)
        tmpl_fld_list = cache.get(tmpl_key)  # type: list
        if tmpl_fld_list is None:
            return result
        else:
            for field_pk in tmpl_fld_list:
                cache.delete(field_pk)
        return result

    def get_data_sources(self):
        fields = self.all_fields
        data_sources = []
        for field in fields:
            ds = field.data_source
            if ds:
                data_sources.append(ds)
        return data_sources

    def get_data_source_related_template(self):
        data_sources = self.fields.filter(local_data_source__contains='template_id')
        related_templates = []
        for ds in data_sources:
            if ds.get('url') == 'data':
                related_template = ds.get('params', {}).get('template_id')
            else:
                continue
            if related_template:
                related_templates.append(related_template)
        return FormTemplate.objects.filter(pk__in=related_templates)

    def copy_to(self, target_id, new_title, creator=None):
        from .utils import copy_template
        return copy_template(self.pk, target_id, new_title, creator=creator)

    def new_empty_serializeable_dict(self) -> Dict[str, Any]:
        result = dict(
            template_id=self.pk,
            sys_id=self.sys_id,
            org_id=self.org_id,
            biz_id=self.biz_id,
            src_id=self.src_id,
        )
        for field in self.all_fields:
            result[field.alias] = None
        return result

    def new_empty_form_dict(self) -> Dict[str, Any]:
        result = dict(
            template_id=self.pk,
            sys_id=self.sys_id,
            org_id=self.org_id,
            biz_id=self.biz_id,
            src_id=self.src_id,
        )
        for field in self.all_fields:
            result[field.col_name] = None
        return result

    def new_empty_form_instance(self):
        field_dict = self.new_empty_form_dict()
        instance = self.get_model()(**field_dict)
        return instance


class FormAggrgateFields(models.Model):
    """模板聚合字段"""
    AGGR_TYPES = (
        ('count', '去重计数'),
        ('sum', '求和'),
        ('avg', '平均值'),
        ('max', '最大值'),
        ('min', '最小值'),
    )

    id = TableNamePKField('FA')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    src_id = models.IntegerField('分区ID', default=0, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    template = models.ForeignKey(
        'FormTemplate', on_delete=models.CASCADE, related_name='aggregate_fields', help_text='模板ID', db_constraint=False
    )
    field = models.ForeignKey(
        'FormFields', on_delete=models.CASCADE, related_name='+', help_text='字段ID', db_constraint=False
    )
    aggr_type = models.CharField('聚合类型', max_length=128, choices=AGGR_TYPES, null=True, blank=True, help_text='聚合类型')
    aggr_name = models.CharField('聚合名称', max_length=128, null=True, blank=True, help_text='聚合名称')
    description = models.CharField('描述', max_length=1023, null=True, blank=True, help_text='描述')

    class Meta:
        verbose_name = '02.模板聚合字段'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.template_id}-{self.field.col_name}'


class ManyToManyData(models.Model):
    """多对多数据"""
    id = TableNamePKField('MTM')
    m_from = models.CharField('M1 ID', db_column='from_id', max_length=32, db_index=True, null=False, blank=False)
    m_to = models.CharField('M2 ID', db_column='to_id', max_length=32, db_index=True, null=False, blank=False)
    m_from_field = models.ForeignKey('FormFields', on_delete=models.CASCADE, related_name='+', db_constraint=False, null=True, blank=True)

    class Meta:
        db_table = 'formtemplate_mtm'
        verbose_name = '03.多对多数据'
        verbose_name_plural = verbose_name


# 表单数据表
class FormData(models.Model):
    """表单数据表"""
    id = TableNamePKField('D')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    src_id = models.IntegerField('分区ID', default=0, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='formdata',
        help_text='用户ID', verbose_name='usercenter_user.id', db_constraint=False, db_index=True
    )
    department = models.ForeignKey(
        'usercenter.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='formdata',
        help_text='部门ID', verbose_name='usercenter_department.id', db_constraint=False, db_index=True
    )
    template = models.ForeignKey(
        'FormTemplate', related_name='data', verbose_name='模版',
        on_delete=models.SET_NULL, null=True, blank=True, help_text='模版ID', db_constraint=False
    )
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True, help_text='父级表单ID'
    )
    obj_id = models.CharField('外键字段', max_length=32, null=True, blank=True, help_text='保存人表、物表、服务表、机构表数据ID')
    create_time = models.DateTimeField(default=timezone.now, help_text='创建时间')

    longitude = models.FloatField('经度', null=True, blank=True, db_index=True, help_text='经度 idx')
    latitude = models.FloatField('纬度', null=True, blank=True, db_index=True, help_text='纬度 idx')
    altitude = models.FloatField('海拔', null=True, blank=True, db_index=True, help_text='海拔 idx')

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

    text_01 = models.TextField('Text 01', null=True, blank=True)

    date_01 = models.DateField('Date 01', null=True, blank=True, db_index=True, help_text='idx')
    date_02 = models.DateField('Date 02', null=True, blank=True, db_index=True, help_text='idx')
    date_03 = models.DateField('Date 03', null=True, blank=True, db_index=True, help_text='idx')
    date_04 = models.DateField('Date 04', null=True, blank=True, db_index=True, help_text='idx')
    date_05 = models.DateField('Date 05', null=True, blank=True, db_index=True, help_text='idx')
    date_06 = models.DateField('Date 06', null=True, blank=True)
    date_07 = models.DateField('Date 07', null=True, blank=True)
    date_08 = models.DateField('Date 08', null=True, blank=True)
    date_09 = models.DateField('Date 09', null=True, blank=True)
    date_10 = models.DateField('Date 10', null=True, blank=True)

    datetime_01 = models.DateTimeField('DateTime 01', null=True, blank=True, db_index=True, help_text='idx')
    datetime_02 = models.DateTimeField('DateTime 02', null=True, blank=True, db_index=True, help_text='idx')
    datetime_03 = models.DateTimeField('DateTime 03', null=True, blank=True)
    datetime_04 = models.DateTimeField('DateTime 04', null=True, blank=True)
    datetime_05 = models.DateTimeField('DateTime 05', null=True, blank=True)
    datetime_06 = models.DateTimeField('DateTime 06', null=True, blank=True)
    datetime_07 = models.DateTimeField('DateTime 07', null=True, blank=True)
    datetime_08 = models.DateTimeField('DateTime 08', null=True, blank=True)
    datetime_09 = models.DateTimeField('DateTime 09', null=True, blank=True)
    datetime_10 = models.DateTimeField('DateTime 10', null=True, blank=True)

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
    int_11 = models.BigIntegerField('Int 11', null=True, blank=True)
    int_12 = models.BigIntegerField('Int 12', null=True, blank=True)
    int_13 = models.BigIntegerField('Int 13', null=True, blank=True)
    int_14 = models.BigIntegerField('Int 14', null=True, blank=True)
    int_15 = models.BigIntegerField('Int 15', null=True, blank=True)
    int_16 = models.BigIntegerField('Int 16', null=True, blank=True)
    int_17 = models.BigIntegerField('Int 17', null=True, blank=True)
    int_18 = models.BigIntegerField('Int 18', null=True, blank=True)
    int_19 = models.BigIntegerField('Int 19', null=True, blank=True)
    int_20 = models.BigIntegerField('Int 20', null=True, blank=True)

    float_01 = models.DecimalField('Float 01', max_digits=16, decimal_places=4, null=True, blank=True, db_index=True, help_text='idx')
    float_02 = models.DecimalField('Float 02', max_digits=16, decimal_places=4, null=True, blank=True, db_index=True, help_text='idx')
    float_03 = models.DecimalField('Float 03', max_digits=16, decimal_places=4, null=True, blank=True)
    float_04 = models.DecimalField('Float 04', max_digits=16, decimal_places=4, null=True, blank=True)
    float_05 = models.DecimalField('Float 05', max_digits=16, decimal_places=4, null=True, blank=True)
    float_06 = models.DecimalField('Float 06', max_digits=16, decimal_places=4, null=True, blank=True)
    float_07 = models.DecimalField('Float 07', max_digits=16, decimal_places=4, null=True, blank=True)
    float_08 = models.DecimalField('Float 08', max_digits=16, decimal_places=4, null=True, blank=True)
    float_09 = models.DecimalField('Float 09', max_digits=16, decimal_places=4, null=True, blank=True)
    float_10 = models.DecimalField('Float 10', max_digits=16, decimal_places=4, null=True, blank=True)

    class Meta:
        verbose_name = '04.表单数据表'
        verbose_name_plural = verbose_name
        db_table = 'formtemplate_formdata'
        managed = False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.src_id:
            self.src_id = self.org_id or 0
        super().save(force_insert, force_update, using, update_fields)

    @property
    def template_field_names(self):
        temp = self.template
        if not temp:
            return None
        return temp.field_names

    @property
    def user_display(self):
        return self.user_full_name if hasattr(self, 'user_full_name') else ''

    @property
    def department_display(self):
        return self.department_name if hasattr(self, 'department_name') else ''


# 表单数据报表
class FormDataReportConf(models.Model):
    """表单数据报表"""
    id = TableNamePKField('report')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    report_id = models.IntegerField('报表ID', default=1, db_index=True, unique=True)
    report_name = models.CharField('报表名称', max_length=31, null=True, blank=True, db_index=True, help_text='报表名称')
    report_remark = models.TextField('报表说明', null=True, blank=True, help_text='报表说明')
    form_template = models.ForeignKey('FormTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    arguments = models.TextField('参数定义', null=True, blank=True, help_text='参数定义')
    data_struct = models.TextField('数据定义', null=True, blank=True, help_text='数据定义')
    charts_struct = models.TextField('图表定义', null=True, blank=True, help_text='图表定义')
    permission = models.ForeignKey(
        'usercenter.FuncPermission', on_delete=models.SET_NULL, null=True, blank=True, help_text='功能模块',
        db_constraint=False, db_index=True
    )

    creator = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL, null=True, blank=True, help_text='创建人', db_constraint=False
    )

    class Meta:
        verbose_name = '05.表单数据报表'
        verbose_name_plural = verbose_name
