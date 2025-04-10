from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from . import models


class RefreshLastPointSerializer(serializers.Serializer):
    sn = serializers.ListField(
        child=serializers.CharField(allow_blank=False), allow_empty=False, required=True
    )
    sys_id = serializers.IntegerField(required=True, allow_null=False)
    org_id = serializers.IntegerField(required=True, allow_null=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LastPointSerializer(serializers.Serializer):
    sn = serializers.ListField(
        child=serializers.CharField(allow_blank=False), allow_empty=False, required=True
    )
    sys_id = serializers.IntegerField(required=True, allow_null=False)
    org_id = serializers.IntegerField(required=True, allow_null=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PointSerializer(ModelSerializer):
    coordinate = serializers.SerializerMethodField()
    class Meta:
        model = models.Point
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'sn',
            'category',
            'sdk_name',
            'coordinate_name',
            'coordinate',
            'longitude',
            'latitude',
            'altitude',
            'direction',
            'velocity',
            'acceleration',
            'create_time',
            'client_time',
            'field_01',
            'field_02',
            'field_03',
            'text_01',
        )

    def get_coordinate(self, obj):
        if obj.longitude and obj.latitude:
            return [obj.longitude, obj.latitude]
        return None


class PolygonSerializer(ModelSerializer):
    line = serializers.JSONField()
    line_style = serializers.JSONField(required=False)

    class Meta:
        model = models.Polygon
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'sn',
            'category',
            'create_time',
            'line',
            'center',
            'line_style',
            'field_01',
            'field_02',
            'field_03',
            'text_01',
        )
