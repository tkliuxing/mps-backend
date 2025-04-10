from utility.db_fields import TableNamePKField
from django.db import models
from django.utils import timezone


class Point(models.Model):
    """地图标记记录"""
    id = TableNamePKField('point')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    sn = models.CharField('SN', max_length=128, db_index=True, null=True, blank=True, help_text='SN')
    category = models.CharField('类别', null=True, blank=True, max_length=128, db_index=True, help_text='类别 idx')
    sdk_name = models.CharField('定位组件名称', max_length=32, default='amap', db_index=True, help_text='定位组件名称')
    coordinate_name = models.CharField('坐标系名称', max_length=32, default='GCJ02', db_index=True, help_text='坐标系名称')
    longitude = models.CharField('经度', max_length=32, db_index=True, null=True, blank=True, help_text='经度 idx')
    latitude = models.CharField('纬度', max_length=32, db_index=True, null=True, blank=True, help_text='纬度 idx')
    radius = models.FloatField('半径', db_index=True, null=True, blank=True, help_text='半径 idx')
    altitude = models.FloatField('海拔', db_index=True, null=True, blank=True, help_text='海拔 idx')
    direction = models.FloatField('方向角', db_index=True, null=True, blank=True, help_text='方向角')
    velocity = models.FloatField('速度', db_index=True, null=True, blank=True, help_text='速度')
    acceleration = models.FloatField('加速度', db_index=True, null=True, blank=True, help_text='加速度')
    create_time = models.DateTimeField('服务器时间', auto_now_add=True, db_index=True, help_text='服务器时间')
    client_time = models.DateTimeField('客户端时间', default=timezone.now, db_index=True, help_text='客户端时间')

    field_01 = models.CharField('Field 01', max_length=128, db_index=True, null=True, blank=True, help_text='idx')
    field_02 = models.CharField('Field 02', max_length=128, db_index=True, null=True, blank=True, help_text='idx')
    field_03 = models.CharField('Field 03', max_length=128, db_index=True, null=True, blank=True, help_text='idx')

    text_01 = models.TextField('Text_01', null=True, blank=True)

    class Meta:
        verbose_name = '01.地图标记信息'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def within_polygon(self, polygon: 'Polygon'):
        """判断点是否在多边形内"""
        return polygon.contains_point(self)


class Polygon(models.Model):
    """地图多边形"""
    id = TableNamePKField('point')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    sn = models.CharField('SN', max_length=128, db_index=True, null=True, blank=True, help_text='SN')
    category = models.CharField('类别', null=True, blank=True, max_length=128, db_index=True, help_text='类别 idx')
    coordinate_name = models.CharField('坐标系名称', max_length=32, default='GCJ02', db_index=True, help_text='坐标系名称')
    line = models.TextField('多边形坐标', null=True, blank=True, help_text='多边形坐标')
    line_style = models.TextField('多边形样式', null=True, blank=True, help_text='多边形样式')
    create_time = models.DateTimeField('服务器时间', auto_now_add=True, db_index=True, help_text='服务器时间')

    field_01 = models.CharField('Field 01', max_length=128, db_index=True, null=True, blank=True, help_text='idx')
    field_02 = models.CharField('Field 02', max_length=128, db_index=True, null=True, blank=True, help_text='idx')
    field_03 = models.CharField('Field 03', max_length=128, db_index=True, null=True, blank=True, help_text='idx')

    text_01 = models.TextField('Text_01', null=True, blank=True)

    class Meta:
        verbose_name = '02.地图多边形信息'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    @property
    def center(self):
        """计算多边形中心点"""
        import json
        from shapely.geometry import Polygon
        if not self.line:
            return None
        line = self.line
        if isinstance(line, str):
            line = json.loads(line)
        if not isinstance(line, list):
            return []
        if len(line) < 3:
            return []
        polygon = Polygon([[i[0], i[1]] for i in line])
        center = polygon.centroid
        return [center.x, center.y]

    def contains_point(self, point: Point):
        """判断点是否在多边形内"""
        import json
        from shapely.geometry import Point as SPoint, Polygon
        if not self.line:
            return False
        line = self.line
        if isinstance(line, str):
            line = json.loads(line)
        if not isinstance(line, list):
            return False
        if len(line) < 3:
            return False
        polygon = Polygon([[i[0], i[1]] for i in line])
        point = SPoint([float(point.longitude), float(point.latitude)])
        return polygon.contains(point)
