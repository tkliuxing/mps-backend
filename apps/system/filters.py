import django_filters

from utility.filter_fields import CharInFilter
from . import models


class SystemFilterSet(django_filters.FilterSet):
    create_time = django_filters.filters.DateFromToRangeFilter(field_name='create_time', label='创建时间')
    update_time = django_filters.filters.DateFromToRangeFilter(field_name='update_time', label='修改时间')

    class Meta:
        model = models.System
        fields = (
            'sys_id',
            'name',
            'create_time',
            'update_time',
        )


class SMSConfigFilterSet(django_filters.FilterSet):
    sys_id = django_filters.NumberFilter(
        field_name='system', lookup_expr='sys_id'
    )

    class Meta:
        model = models.SMSConfig
        fields = (
            'system',
            'name',
            'sms_type',
            'is_enabled',
        )


class WechatConfigFilterSet(django_filters.FilterSet):
    class Meta:
        model = models.WechatConfig
        fields = (
            'system',
            'is_default',
        )


class SystemProjectFilterSet(django_filters.FilterSet):
    sys_id = django_filters.NumberFilter(field_name='system', lookup_expr='sys_id')

    class Meta:
        model = models.SystemProject
        fields = (
            'biz_id',
            'system',
            'project_type',
            'pm_name',
        )


class SystemProjectRouterFilterSet(django_filters.FilterSet):
    is_root = django_filters.BooleanFilter(field_name='parent', lookup_expr='isnull')

    class Meta:
        model = models.SystemProjectRouter
        fields = ('sys_id', 'project')


class SystemProjectMenuFilterSet(django_filters.FilterSet):
    is_root = django_filters.BooleanFilter(field_name='parent', lookup_expr='isnull')

    class Meta:
        model = models.SystemProjectMenu
        fields = ('sys_id', 'project')


class SystemLogFilterSet(django_filters.FilterSet):
    create_time = django_filters.DateTimeFromToRangeFilter()
    log_type = CharInFilter()

    class Meta:
        model = models.SystemLog
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'log_level',
            'user',
            'user_name',
            'template_id',
        )
