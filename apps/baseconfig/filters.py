import django_filters
from utility.filter_fields import CharInFilter
from . import models


class BaseTreeFilterSet(django_filters.FilterSet):
    noroot = django_filters.BooleanFilter(
        method='filter_noroot', help_text='是否返回根节点(True返回从第1级开始的节点，False只返回根节点)',
        required=True,
    )
    isroot = django_filters.BooleanFilter(
        field_name='parent', lookup_expr='isnull',
        help_text='是否返回根节点(true只返回根节点，false返回从第1级开始的节点)',
        required=True,
    )
    parent_name = django_filters.CharFilter(
        field_name='parent__name',
        help_text='父节点名称',
        label='父节点名称',
    )
    is_system = django_filters.BooleanFilter(
        field_name='sys_id', method='filter_is_system',
        help_text='是否系统分类',
        label='是否系统分类',
    )
    level_in = django_filters.CharFilter(
        field_name='level',
        help_text='层级',
        label='层级',
    )

    class Meta:
        model = models.BaseTree
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'parent',
            'name',
            'field_01',
            'field_02',
            'field_03',
            'int_01',
            'float_01',
            'text_01',
            'level',
        )

    def filter_is_system(self, qs, name, value):
        if value is True:
            return qs.filter(org_id=0)
        else:
            return qs.filter(org_id__gt=0)

    def filter_noroot(self, qs, name, value):
        if value is True:
            return qs.filter(level=1)
        else:
            return qs.filter(parent__isnull=True)


class FlatBaseTreeFilterSet(django_filters.FilterSet):
    parent_name = django_filters.CharFilter(
        field_name='parent__name',
        help_text='父节点名称',
        label='父节点名称',
    )
    noroot = django_filters.BooleanFilter(
        method='filter_noroot', help_text='是否返回根节点(True返回从第1级开始的节点，False只返回根节点)',
        required=True,
    )
    isroot = django_filters.BooleanFilter(
        field_name='parent', lookup_expr='isnull',
        help_text='是否返回根节点(true只返回根节点，false返回从第1级开始的节点)',
        required=True,
    )
    is_system = django_filters.BooleanFilter(
        field_name='sys_id', method='filter_is_system',
        help_text='是否系统分类',
        label='是否系统分类',
    )
    root_id = django_filters.CharFilter(
        field_name='sys_id', method='filter_root_id',
        help_text='根节点ID',
        label='根节点ID',
    )
    level_in = django_filters.CharFilter(
        field_name='level',
        help_text='层级',
        label='层级',
    )

    class Meta:
        model = models.BaseTree
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'parent',
            'tree_id',
            'name',
            'field_01',
            'field_02',
            'field_03',
            'int_01',
            'float_01',
            'text_01',
            'level',
        )

    def filter_root_id(self, qs, name, value):
        try:
            root_node = models.BaseTree.objects.get(pk=value)
            tree_id = root_node.tree_id
            return qs.filter(tree_id=tree_id)
        except models.BaseTree.DoesNotExist:
            return qs

    def filter_noroot(self, qs, name, value):
        if value is True:
            return qs.filter(level=1)
        else:
            return qs.filter(parent__isnull=True)

    def filter_is_system(self, qs, name, value):
        if value is True:
            return qs.filter(org_id=0)
        else:
            return qs.filter(org_id__gt=0)


class BaseConfigFileUploadFilterSet(django_filters.FilterSet):
    template = CharInFilter()
    obj_id = CharInFilter()
    category = CharInFilter()
    user = CharInFilter()
    pk_in = CharInFilter(field_name='pk', lookup_expr='in')

    class Meta:
        model = models.BaseConfigFileUpload
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
        )
