import django_filters
from . import models


class ParametersFilterSet(django_filters.FilterSet):
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

    class Meta:
        model = models.Parameters
        fields = (
            'category',
            'parent',
            'name',
        )

    def filter_noroot(self, qs, name, value):
        if value is True:
            return qs.filter(level=1)
        else:
            return qs.filter(parent__isnull=True)

