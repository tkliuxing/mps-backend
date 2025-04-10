import django_filters
from django.db.models import Q

from utility.filter_fields import CharInFilter
from . import models


class NoticeFilterSet(django_filters.FilterSet):
    msg_type = CharInFilter(field_name='msg_type')
    obj_type = CharInFilter(field_name='obj_type')
    obj_id = CharInFilter(field_name='obj_id')
    public_user = CharInFilter(field_name='public_user')
    department_in = django_filters.CharFilter(
        method='filter_department_in', label='接收用户部门', help_text='部门ID，多个用逗号分隔'
    )
    from_department_in = django_filters.CharFilter(
        method='filter_from_department_in', label='发送用户部门', help_text='部门ID，多个用逗号分隔'
    )

    class Meta:
        model = models.MailBox
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'is_published',
            'department_range',
        )

    def filter_department_in(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(user__department_id__in=value.split(',')) | Q(departments__id__in=value.split(','))
            )
        return queryset

    def filter_from_department_in(self, queryset, name, value):
        if value:
            return queryset.filter(
                from_user__department_id__in=value.split(',')
            )
        return queryset


class MailBoxFilter(django_filters.FilterSet):
    user_department_id = CharInFilter(field_name='user__department__id', label='接收用户部门', help_text='部门ID，多个用逗号分隔')
    from_user_department_id = CharInFilter(field_name='from_user__department__id', label='发送用户部门', help_text='部门ID，多个用逗号分隔')

    class Meta:
        model = models.MailBox
        fields = (
            'user_id', 'from_user_id', 'sys_id', 'org_id', 'biz_id', 'obj_id', 'is_read', 'obj_type',
        )


class NoticePoolFilterSet(django_filters.FilterSet):
    pk = CharInFilter(field_name='pk')
    send_time = django_filters.DateTimeFromToRangeFilter(field_name='send_time', label='发送时间')
    send_to = CharInFilter(field_name='send_to__id', label='发送给用户', help_text='用户ID，多个用逗号分隔')

    class Meta:
        model = models.NoticePool
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'obj_id',
            'obj_type',
            'msg_type',
            'title',
            'content',
            'is_sent',
            'is_circulation',
            'from_user',
            'from_user_display',
            'is_public',
            'create_time',
            'last_modify',
            'channel',
        )
