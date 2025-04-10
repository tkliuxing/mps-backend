import django_filters
from utility.filter_fields import CharInFilter
from .models import Account, AccountStatements


class AccountFilterSet(django_filters.FilterSet):
    obj_id = CharInFilter(field_name='obj_id')
    user = CharInFilter(field_name='user_id')
    acc_1_name = CharInFilter(field_name='acc_1_name')
    acc_2_name = CharInFilter(field_name='acc_2_name')
    acc_3_name = CharInFilter(field_name='acc_3_name')
    acc_1_type = CharInFilter(field_name='acc_1_type')
    acc_2_type = CharInFilter(field_name='acc_2_type')
    acc_3_type = CharInFilter(field_name='acc_3_type')
    jifen_acc = CharInFilter(field_name='jifen_acc')
    create_time_after = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    create_time_before = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    acc_1_balance = django_filters.NumericRangeFilter(field_name='acc_1_balance')
    acc_2_balance = django_filters.NumericRangeFilter(field_name='acc_2_balance')
    acc_3_balance = django_filters.NumericRangeFilter(field_name='acc_3_balance')
    acc_1_lock = django_filters.NumericRangeFilter(field_name='acc_1_lock')
    acc_2_lock = django_filters.NumericRangeFilter(field_name='acc_2_lock')
    acc_3_lock = django_filters.NumericRangeFilter(field_name='acc_3_lock')

    class Meta:
        model = Account
        fields = (
            'org_id',
            'sys_id',
            'biz_id',
            'src_id',
        )


class AccountStatementsFilterSet(django_filters.FilterSet):
    end_time = django_filters.DateTimeFromToRangeFilter()
    create_time = django_filters.DateTimeFromToRangeFilter()
    update_time = django_filters.DateTimeFromToRangeFilter()
    acc = CharInFilter(field_name='acc_id')
    acc_name = CharInFilter(field_name='acc_name')
    record_type = CharInFilter(field_name='record_type')

    field_01_like = django_filters.CharFilter(field_name='field_01', lookup_expr='icontains')
    field_02_like = django_filters.CharFilter(field_name='field_01', lookup_expr='icontains')
    field_03_like = django_filters.CharFilter(field_name='field_01', lookup_expr='icontains')
    field_04_like = django_filters.CharFilter(field_name='field_01', lookup_expr='icontains')
    field_05_like = django_filters.CharFilter(field_name='field_01', lookup_expr='icontains')

    class Meta:
        model = AccountStatements
        fields = (
            'org_id',
            'sys_id',
            'biz_id',
            'src_id',
            'order_num',
            'field_01',
            'field_02',
            'field_03',
            'field_04',
            'field_05',
            'float_01',
            'float_02',
            'float_03',
            'float_04',
            'float_05',
        )
