from rest_framework.utils.json import dumps, loads
from django_redis import get_redis_connection
from django.db.models import QuerySet
from . import serializers
from . import models

cache = get_redis_connection("default")


def get_point_data(gps_sn, sys_id):
    key = f'gps-point-{gps_sn}'
    val = cache.get(key)
    val = loads(val) if val else None
    if val and str(val.get('sys_id')) == str(sys_id):
        return val
    instance = models.Point()
    return serializers.PointSerializer(instance=instance).data


def refresh_last_point_all():
    sql = """
        with T as (
          select
            *,
            row_number() over (
              partition by fd.sn
              order by
                fd.create_time desc
            ) as rownum
          from
            gps_point as fd
        )
        select * from T where rownum = 1
    """
    qs = models.Point.objects.raw(sql)
    cnt = 0
    for i in qs:
        cache.set(f'gps-point-{i.sn}', dumps(serializers.PointSerializer(instance=i).data))
        # print('sn:', i.sn)
        cnt += 1
    return cnt


def refresh_last_point(sys_id, org_id, sn_list):
    qs = get_last_points(sys_id, org_id, sn_list)
    cnt = 0
    for i in qs:
        cache.set(f'gps-point-{i.sn}', dumps(serializers.PointSerializer(instance=i).data))
        cnt += 1
    return cnt


def get_last_points(sys_id, org_id, sn_list) -> QuerySet[models.Point]:
    sql = """
        with T as (
          select
            *,
            row_number() over (
              partition by fd.sn
              order by
                fd.create_time desc
            ) as rownum
          from
            gps_point as fd
          where
            fd.org_id = %s and 
            fd.sys_id = %s and
            fd.sn in %s
        )
        select * from T where rownum = 1
    """
    qs = models.Point.objects.raw(sql, (org_id, sys_id, tuple(sn_list),))
    return qs
