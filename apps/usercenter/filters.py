import django_filters
from utility.filter_fields import CharInFilter
from baseconfig.models import BaseTree
from . import models


class FuncPermissionTreeFilterSet(django_filters.FilterSet):
    pm_name = django_filters.CharFilter(method='filter_pm_name', label='项目绑定名称')

    class Meta:
        model = models.FuncPermission
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'level',
            'parent',
            'level',
        )

    def filter_pm_name(self, queryset, name, value):
        from system.models import SystemProject
        sp = SystemProject.objects.filter(pm_name=value).order_by('system__sys_id').distinct('system__sys_id').values_list('system__sys_id', flat=True)
        return queryset.filter(sys_id__in=sp)


class DepartmentFilterSet(django_filters.FilterSet):
    pk = CharInFilter(field_name='pk')

    class Meta:
        model = models.Department
        fields = (
            'category',
            'sys_id',
            'org_id',
            'parent',
            'level',
            'name',
        )


class UserFilterSet(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='contains', label='姓名')
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=BaseTree.objects.all(), help_text='分类'
    )
    group_name = django_filters.CharFilter(
        field_name='func_groups__name'
    )
    group_isnull = django_filters.BooleanFilter(
        field_name='func_groups',
        lookup_expr='isnull',
        label='是否无角色组'
    )
    department = CharInFilter(field_name='department_id')
    o = django_filters.OrderingFilter(
        fields=(
            ('sort_num', 'sort_num'),
            ('username', 'username'),
            ('full_name', 'full_name'),
            ('department', 'department'),
        )
    )

    class Meta:
        model = models.User
        fields = (
            'sys_id',
            'org_id',
            'username',
            'mobile',
            'status',
            'email',
            'full_name',
            'is_active',
            'is_department_manager',
        )
