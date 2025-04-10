import django_filters

from utility.filter_fields import CharInFilter
from . import models


class SocialDynamicFilterSet(django_filters.FilterSet):
    department_in = CharInFilter(
        field_name='user__department__id',
    )
    department = django_filters.CharFilter(
        field_name='user__department__id',
    )
    
    class Meta:
        model = models.SocialDynamic
        fields = ('sys_id', 'org_id', 'biz_id', 'src_id', 'user', 'is_anonymous', 'is_hot', 'is_deleted')
