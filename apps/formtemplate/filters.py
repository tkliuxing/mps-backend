import django_filters
from utility.filter_fields import CharInFilter
from . import models


class FormTemplateFilterSet(django_filters.FilterSet):
    department = CharInFilter(field_name='department')

    class Meta:
        model = models.FormTemplate
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'fenlei',
            'title',
            'form_type',
            'need_login',
        )
