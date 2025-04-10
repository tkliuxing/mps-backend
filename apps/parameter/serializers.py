from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from . import models


class ParametersCategorysSerializer(serializers.Serializer):
    """常参表分类列表"""
    category = serializers.CharField(read_only=True, help_text='分类名称')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class FlatParametersSerializer(ModelSerializer):
    """树形常参表"""

    class Meta:
        model = models.Parameters
        fields = (
            'pk',
            'category',
            'name',
            'value',
            'field_01',
            'field_02',
            'field_03',
            'parent',
            'remark',
            'field_json',
        )


class ParametersSerializer(ModelSerializer):
    """树形常参表"""
    items = serializers.SerializerMethodField()

    class Meta:
        model = models.Parameters
        fields = (
            'pk',
            'category',
            'name',
            'value',
            'field_01',
            'field_02',
            'field_03',
            'parent',
            'remark',
            'field_json',
            'items',
        )

    def get_items(self, obj):
        children = obj.children.all()
        childrens = ParametersSerializer(children, many=True).data
        result = []
        result.extend(childrens)
        return result


class FlatParametersSerializer(serializers.ModelSerializer):
    """平铺常参表"""

    class Meta:
        model = models.Parameters
        fields = (
            'pk',
            'category',
            'name',
            'value',
            'field_01',
            'field_02',
            'field_03',
            'parent',
            'remark',
            'field_json',
        )


class ParametersToBaseTreeSerializer(serializers.Serializer):
    """复制到分类树"""
    id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sys_id = serializers.IntegerField(required=True)
    org_id = serializers.IntegerField(required=True)
    biz_id = serializers.IntegerField(required=True)

    def valid_category(self, value):
        objs = models.Parameters.objects.filter(category=value)
        if not objs:
            raise serializers.ValidationError('分类不存在！')
        return value

    def valid_id(self, value):
        try:
            models.Parameters.objects.get(pk=value)
        except:
            raise serializers.ValidationError('id not found!')
        return value

    def validate(self, attrs):
        from baseconfig.models import BaseTree
        if attrs.get('id'):
            obj = models.Parameters.objects.get(pk=attrs['id'])
            sys_id = attrs['sys_id']
            org_id = attrs['sys_id']
            name = obj.name
            if BaseTree.objects.filter(sys_id=sys_id, org_id=org_id, name=name, parent__isnull=True):
                raise serializers.ValidationError('节点名称已存在！')
            attrs['obj'] = obj
            if attrs.get('category'):
                attrs.pop('category')
            return attrs
        if attrs.get('category'):
            attrs['obj'] = models.Parameters.objects.filter(category=attrs['category']).first()
            return attrs
        raise serializers.ValidationError('id 或 category 必须填写一个！')

    def create(self, validated_data):
        obj = validated_data.pop('obj')
        sys_id = validated_data['sys_id']
        org_id = validated_data['org_id']
        biz_id = validated_data['biz_id']
        if not validated_data.get('category'):
            obj.to_basetree(sys_id, org_id, biz_id)
            return validated_data
        models.Parameters.category_to_basetree(
            validated_data['category'],
            sys_id,
            org_id,
            biz_id,
        )
        return validated_data

    def update(self, instance, validated_data):
        return None
