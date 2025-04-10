import django_filters
from utility.filter_fields import CharInFilter
from . import models


class PointFilterSet(django_filters.FilterSet):
    create_time = django_filters.DateTimeFromToRangeFilter()
    client_time = django_filters.DateTimeFromToRangeFilter()
    longitude = django_filters.NumericRangeFilter()
    latitude = django_filters.NumericRangeFilter()
    altitude = django_filters.NumericRangeFilter()
    direction = django_filters.NumericRangeFilter()
    velocity = django_filters.NumericRangeFilter()
    acceleration = django_filters.NumericRangeFilter()
    sn = CharInFilter()
    category = CharInFilter()
    o = django_filters.OrderingFilter(
        fields=(
            ('create_time', 'create_time',),
            ('client_time', 'client_time',),
            ('sn', 'sn',),
        )
    )

    class Meta:
        model = models.Point
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'sn',
        )


class PointTimeFilterSet(django_filters.FilterSet):
    time_point = django_filters.DateTimeFilter(method='filter_time_point')

    class Meta:
        model = models.Point
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'sn',
        )

    def filter_time_point(self, qs, name, value):
        # src_id = value.strftime('%j')
        src_id=1
        return qs.filter(client_time__lte=value, src_id=src_id).order_by('-create_time')


class PolygonFilterSet(django_filters.FilterSet):
    create_time = django_filters.DateTimeFromToRangeFilter()
    client_time = django_filters.DateTimeFromToRangeFilter()
    sn = CharInFilter()
    category = CharInFilter()
    o = django_filters.OrderingFilter(
        fields=(
            ('create_time', 'create_time',),
            ('client_time', 'client_time',),
            ('sn', 'sn',),
        )
    )

    class Meta:
        model = models.Polygon
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
            'sn',
        )


class LastPointFilterSet(django_filters.FilterSet):
    sn = django_filters.CharFilter(
        field_name='sn', method='filter_sn', label='sn，可多条'
    )

    date_time = django_filters.DateTimeFilter(
        field_name='create_time', method='filter_date_time', label='最后更新时间'
    )

    class Meta:
        model = models.Point
        fields = (
            'sys_id',
            'org_id',
            'biz_id',
        )

    def filter_date_time(self, qs, name, value):
        return qs

    def filter_sn(self, qs, name, val):
        sn_list = self.request.data.get('sn', [])
        val_list = [i for i in set(sn_list) if i and i != 'null']
        return qs.filter(geo_type='point').filter(sn__in=val_list)
