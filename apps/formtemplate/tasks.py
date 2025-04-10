"""
表单模板相关的异步任务模块。

此模块包含了处理表单模板相关异步操作的任务，包括关联删除和文件模板更新等功能。
"""

import re
from celery import shared_task
from celery.utils.log import get_task_logger
from service.models import Services
from org.models import Org
from customer.models import Customer
from goods.models import Goods
from formtemplate.models import FormTemplate, FormFields, FormData
from baseconfig.models import BaseConfigFileUpload

try:
    from llm.tasks import create_dify_document_from_file
except ImportError:
    create_dify_document_from_file = None

# 用于匹配文件上传ID的正则表达式
FILE_UPLOAD_ID_REGEX = re.compile(r'"(files\d{18})"')


@shared_task
def related_delete(template_id: str, obj_id: str):
    """
    删除与指定模板和对象ID相关的所有关联数据。

    Args:
        template_id (str): 表单模板ID
        obj_id (str): 关联对象ID

    此任务会：
    1. 查找所有使用该模板ID的关联字段
    2. 清除相关模型中的obj_id引用
    3. 删除相关的文件上传记录
    """
    logger = get_task_logger('formtemplate.tasks.related_delete')

    # 查找所有使用该模板ID的关联字段
    rel_objs = FormFields.objects.filter(related_template_id=template_id, col_name='obj_id').values('template_id').distinct()
    if rel_objs:
        # 清除相关模型中的obj_id引用
        FormData.objects.filter(obj_id=obj_id).update(obj_id=None)
        Services.objects.filter(obj_id=obj_id).update(obj_id=None)
        Org.objects.filter(obj_id=obj_id).update(obj_id=None)
        Customer.objects.filter(obj_id=obj_id).update(obj_id=None)
        Goods.objects.filter(obj_id=obj_id).update(obj_id=None)
    logger.info(f'related delete {obj_id} success')

    # 删除相关的文件上传记录
    for bcf in BaseConfigFileUpload.objects.filter(template_id=template_id, obj_id=obj_id):
        try:
            bcf.file.delete()
            bcf.delete()
        except Exception as e:
            logger.error(f'delete file {bcf.file} error: {e}', exc_info=True)


@shared_task
def update_file_template_and_llm(template_id: str, obj_id: str):
    """
    更新文件模板并触发LLM文档创建。

    Args:
        template_id (str): 表单模板ID
        obj_id (str): 关联对象ID

    此任务会：
    1. 查找对象中所有包含文件引用的字符串字段
    2. 更新相关文件记录的模板ID和对象ID
    3. 如果LLM服务可用，为每个文件创建文档
    """
    logger = get_task_logger('formtemplate.tasks.update_file_template_and_llm')
    string_fields_values = []
    file_ids = []

    # 获取模板和对象实例
    obj = FormTemplate.objects.get(pk=template_id).get_model().objects.get(pk=obj_id)

    # 遍历所有字段，查找包含文件引用的字符串字段
    for field in obj._meta.get_fields():
        field_name = field.name
        field_value = getattr(obj, field_name)
        if isinstance(field_value, str) and 'files' in field_value:
            string_fields_values.append(field_value)
    logger.debug(f'string_fields_values: {string_fields_values}')

    # 从字符串字段中提取文件ID
    for string_field_value in string_fields_values:
        file_ids.extend(FILE_UPLOAD_ID_REGEX.findall(string_field_value))
    logger.debug(f'file_ids: {file_ids}')

    # 更新文件记录并触发LLM文档创建
    files = BaseConfigFileUpload.objects.filter(id__in=set(file_ids))
    files.update(template_id=template_id, obj_id=obj_id)
    if create_dify_document_from_file:
        for file_id in files.values_list('id', flat=True):
            create_dify_document_from_file.delay(file_id)
            # create_dify_document_from_file(file_id)
