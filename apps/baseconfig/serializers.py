from rest_framework import serializers
from django.conf import settings

from utility.id_gen import gen_new_id
from . import models


class FlatBaseTreeSerializer(serializers.ModelSerializer):
    """分类树平铺"""
    pk = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = models.BaseTree
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'name',
            'parent',
            'level',
            'description',
            'description_or_name',
            'arguments',
            'leaf',
            'tree_id',
            'field_01',
            'field_02',
            'field_03',
            'int_01',
            'float_01',
            'text_01',
        )

    def validate(self, attrs):
        parent = attrs.get('parent')
        sys_id = attrs.get('sys_id')
        org_id = attrs.get('org_id')
        name = attrs.get('name')
        if parent:
            return attrs
        has_same = attrs.get('pk') and not models.BaseTree.objects.filter(
            pk=attrs['pk']
        ).exists() and models.BaseTree.objects.filter(
            sys_id=sys_id, org_id=org_id, name=name, parent__isnull=True
        ).exists()
        if has_same:
            raise serializers.ValidationError('系统分类名称重复')
        return attrs

    def create(self, validated_data):
        if not validated_data.get('pk'):
            validated_data['pk'] = gen_new_id('bt')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super().update(instance, validated_data)


class BaseTreeSerializer(FlatBaseTreeSerializer):
    """分类树"""
    items = serializers.SerializerMethodField()

    class Meta:
        model = models.BaseTree
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'name',
            'parent',
            'level',
            'description',
            'description_or_name',
            'arguments',
            'items',
            'leaf',
            'tree_id',
            'icon',
            'field_01',
            'field_02',
            'field_03',
            'int_01',
            'float_01',
            'text_01',
        )

    def get_child_serializer_data(self, children):
        return BaseTreeSerializer(children, many=True).data

    def get_items(self, obj):
        children = obj.children.all()
        childrens = self.get_child_serializer_data(children)
        result = []
        result.extend(childrens)
        return result

    def create(self, validated_data):
        if not validated_data.get('pk'):
            validated_data['pk'] = gen_new_id('bt')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'pk' in validated_data:
            validated_data.pop('pk')
        return super().update(instance, validated_data)


class BaseTreeMiniSerializer(BaseTreeSerializer):
    """分类树简要信息"""
    items = serializers.SerializerMethodField()

    class Meta:
        model = models.BaseTree
        fields = (
            'pk',
            'name',
            'description_or_name',
            'parent',
            'level',
            'items',
            'leaf',
            'tree_id',
        )

    def get_child_serializer_data(self, children):
        return BaseTreeMiniSerializer(children, many=True).data


class BaseTreeMoveSerializer(serializers.Serializer):
    POSITION_CHOICES = (
        ('first-child', '第一个子节点'),
        ('last-child', '最后一个子节点'),
        ('left', '之前'),
        ('right', '之后'),
    )
    node = serializers.CharField(
        label='当前节点ID',
        help_text='当前节点ID'
    )
    target = serializers.CharField(
        label='目标节点ID',
        help_text='目标节点ID'
    )
    position = serializers.ChoiceField(
        label='位置',
        help_text='位置',
        choices=POSITION_CHOICES
    )

    def validate(self, attrs):
        try:
            node = models.BaseTree.objects.get(pk=attrs['node'])
        except models.BaseTree.DoesNotExist:
            raise serializers.ValidationError('node 不存在')
        try:
            target = models.BaseTree.objects.get(pk=attrs['target'])
        except models.BaseTree.DoesNotExist:
            raise serializers.ValidationError('target 不存在')
        attrs['node'] = node
        attrs['target'] = target
        return attrs

    def update(self, instance, validated_data):
        target = validated_data['target']
        instance.move_to(target, validated_data['position'])
        return instance

    def create(self, validated_data):
        node = validated_data['node']
        target = validated_data['target']
        node.move_to(target, validated_data['position'])
        return node


class BaseTreeCopySerializer(serializers.Serializer):
    root_node = serializers.PrimaryKeyRelatedField(
        label='根节点ID',
        help_text='根节点ID',
        queryset=models.BaseTree.objects.root_nodes()
    )
    sys_id = serializers.IntegerField(
        label='系统ID',
        help_text='系统ID'
    )
    org_id = serializers.IntegerField(
        label='组织ID',
        help_text='组织ID'
    )
    biz_id = serializers.IntegerField(
        label='业务ID',
        help_text='业务ID'
    )

    def create(self, validated_data):
        root_node = validated_data['root_node']  # type: models.BaseTree
        sys_id = validated_data['sys_id']
        org_id = validated_data['org_id']
        biz_id = validated_data['biz_id']
        new_node = models.copy_tree_node(
            root_node,
            sys_id=sys_id,
            org_id=org_id,
            biz_id=biz_id,
            src_id=root_node.src_id,
        )
        return new_node

    def update(self, instance, validated_data):
        pass


class MyFileField(serializers.FileField):
    def to_representation(self, value):
        # media_url = settings.MEDIA_URL
        try:
            url = value.url
        except AttributeError:
            return None
        return url


class BaseConfigFileUploadSerializer(serializers.ModelSerializer):
    file = MyFileField(
        label='文件',
        help_text='文件',
        required=True,
        use_url=True,
        allow_null=False,
        allow_empty_file=False,
    )
    class Meta:
        model = models.BaseConfigFileUpload
        fields = (
            'pk',
            'file',
            'sys_id',
            'org_id',
            'biz_id',
            'category',
            'template',
            'create_time',
            'file_name',
            'obj_id',
            'is_delete',
            'user',
        )
