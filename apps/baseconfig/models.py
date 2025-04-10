import os
import logging
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from utility.db_fields import TableNamePKField
from utility.id_gen import gen_new_id

logger = logging.getLogger('django')


class BaseTree(MPTTModel):
    """分类树"""
    id = TableNamePKField('bt', editable=True)
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name='上级',
                            db_index=True, on_delete=models.CASCADE, help_text='上级ID parent_id to baseconfig_basetree')
    name = models.CharField('类别名称', max_length=255, null=True, blank=True, help_text='类别名称')
    description = models.TextField('说明', null=True, blank=True, help_text='说明')
    arguments = models.TextField('参数', null=True, blank=True, help_text='参数')
    icon = models.CharField('Icon', max_length=1024, null=True, blank=True)

    field_01 = models.CharField('Field 01', max_length=1024, null=True, blank=True)
    field_02 = models.CharField('Field 02', max_length=1024, null=True, blank=True)
    field_03 = models.CharField('Field 03', max_length=1024, null=True, blank=True)
    int_01 = models.BigIntegerField('Int 01', null=True, blank=True, db_index=True)
    float_01 = models.DecimalField('Float 01', max_digits=16, decimal_places=4, null=True, blank=True)
    text_01 = models.TextField('Text_01', null=True, blank=True)

    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = '分类树'
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['name']

    @property
    def leaf(self):
        return self.is_leaf_node()

    def __str__(self):
        return self.name or 'None'

    def get_path_name(self):
        names = self.get_ancestors(include_self=True).values_list('name', flat=True)
        return "/".join(names)

    @property
    def description_or_name(self):
        return self.description or self.name


def copy_tree_node(node, sys_id, org_id, biz_id, src_id, parent=None):
    new_node = BaseTree(
        id=gen_new_id('bt'),
        sys_id=sys_id,
        org_id=org_id,
        biz_id=biz_id,
        src_id=src_id,
        parent=parent,
        name=node.name,
        description=node.description,
        arguments=node.arguments,
        icon=node.icon,
        field_01=node.field_01,
        field_02=node.field_02,
        field_03=node.field_03,
        int_01=node.int_01,
        float_01=node.float_01,
        text_01=node.text_01,
    )
    new_node.save()
    for child in node.get_children():
        copy_tree_node(child, sys_id=sys_id, org_id=org_id, biz_id=biz_id, src_id=src_id, parent=new_node)
    return new_node


class BaseConfigFileUpload(models.Model):
    id = TableNamePKField('files')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    category = models.ForeignKey(
        'BaseTree', on_delete=models.SET_NULL, null=True, blank=True, help_text='分类',
        db_constraint=False
    )
    template = models.ForeignKey(
        'formtemplate.FormTemplate', on_delete=models.CASCADE, null=True, blank=True, help_text='模板',
        db_constraint=False
    )
    file = models.FileField(
        '文件', upload_to='baseconfigvaluefile/%Y/%m/%d/', max_length=1023, help_text='文件'
    )
    file_name = models.CharField('文件名', max_length=1023, null=True, blank=True, help_text='文件名称')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    obj_id = models.CharField('关联对象ID', max_length=64, null=True, blank=True, db_index=True, help_text='关联对象ID')
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.CASCADE, null=True, blank=True, help_text='用户', db_constraint=False
    )
    dify_document_id = models.CharField('Dify文档ID', max_length=36, null=True, blank=True, help_text='Dify文档ID', db_index=True)
    is_deleted = models.BooleanField('是否删除', default=False, db_index=True)

    class Meta:
        verbose_name = '基础配置项文件'
        verbose_name_plural = verbose_name
        ordering = ['pk']

    @property
    def is_delete(self):
        try:
            return not self.file or not os.path.exists(self.file.path)
        except NotImplementedError:
            return False

    def delete(self, *args, **kwargs):
        if self.dify_document_id:
            try:
                from llm.tasks import delete_dify_document
                delete_dify_document(self.id)
            except Exception as e:
                logger.error(f'BaseConfigFileUpload: Failed to delete Dify document with id {self.id}: {e}', exc_info=True)
        super().delete(*args, **kwargs)
