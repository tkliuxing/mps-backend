import itertools
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField, Serializer
from . import models


class FormFieldsSerializer(ModelSerializer):
    class Meta:
        model = models.FormFields
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'template',
            'related_template',
            'col_title',
            'alias',
            'col_name',
            'in_filter',
            'is_required',
            'is_related',
            'is_vant_show',
            'is_m2m',
            'm2m_model',
            'widget',
            'widget_attr',
            'verify_exp',
            'local_data_source',
            'sort_num',
            'data',
            'desc',
            'unique',
        )


class FormTemplateSerializer(ModelSerializer):
    field = SerializerMethodField()
    aggregate_field = SerializerMethodField()
    children = SerializerMethodField()

    class Meta:
        model = models.FormTemplate
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'fenlei',
            'api_version',
            'api_name',
            'api_path',
            'parent',
            'children',
            'create_time',
            'title',
            'form_type',
            'keyword',
            'remark',
            'table_lines',
            'header_conf',
            'field',
            'aggregate_field',
            'photo',
            'need_login',
            'department',
            'from_template',
            'permission',
            'creator',
        )

    def validate_creator(self, value):
        if value is None:
            return self.context['request'].user
        return value

    def get_children(self, obj: models.FormTemplate):
        return FormTemplateSerializer(obj.children.all(), many=True).data

    def get_field(self, obj: models.FormTemplate):
        fields = obj.all_fields
        fields.sort(key=lambda x: x.sort_num)
        return FormFieldsSerializer(obj.fields.order_by('sort_num'), many=True).data

    def get_aggregate_field(self, obj: models.FormTemplate):
        aggregate_fields = obj.aggregate_fields.all()
        return FormAggrgateFieldsSerializer(aggregate_fields, many=True).data


class FormTemplateMinSerializer(ModelSerializer):
    class Meta:
        model = models.FormTemplate
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'fenlei',
            'api_version',
            'api_name',
            'api_path',
            'parent',
            'create_time',
            'title',
            'form_type',
            'keyword',
            'remark',
            'table_lines',
            'header_conf',
            'photo',
            'need_login',
            'from_template',
        )


class FormAggrgateFieldsSerializer(ModelSerializer):

    class Meta:
        model = models.FormAggrgateFields
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'src_id',
            'biz_id',
            'template',
            'field',
            'aggr_type',
            'aggr_name',
            'description',
        )


class FormTemplateCodeSerializer(ModelSerializer):
    class Meta:
        model = models.FormTemplate
        fields = (
            'pk',
            'code',
        )


class FormDataReportConfSerializer(ModelSerializer):
    class Meta:
        model = models.FormDataReportConf
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'report_id',
            'report_name',
            'report_remark',
            'form_template',
            'arguments',
            'data_struct',
            'charts_struct',
            'permission',
            'creator',
        )

    def validate_creator(self, value):
        if value is None:
            return self.context['request'].user
        return value


class FormTemplateCopySerializer(Serializer):
    form_id = serializers.CharField(required=True, help_text='源表单模板ID')
    target_id = serializers.IntegerField(required=True, help_text='目标系统ID')
    new_title = serializers.CharField(required=True, help_text='目标模板名称')
    pk = serializers.CharField(read_only=True, help_text='新模板ID')

    def validate_form_id(self, value):
        try:
            return models.FormTemplate.objects.get(pk=value)
        except models.FormTemplate.DoesNotExist:
            raise serializers.ValidationError("源表单模板不存在")

    def validate(self, attrs):
        form_id = attrs['form_id']
        target_id = attrs['target_id']
        exist_template = models.FormTemplate.objects.filter(sys_id=target_id, from_template=form_id).first()
        if exist_template and exist_template.sys_id != target_id:
            raise serializers.ValidationError(f"目标系统已存在相同表单模板: {exist_template.title}")
        return attrs

    def create(self, validated_data):
        form_id = validated_data['form_id']
        target_sys_id = validated_data['target_id']
        new_title = validated_data['new_title']
        creator = self.context['request'].user
        new_form_template = form_id.copy_to(target_sys_id, new_title, creator)
        return FormTemplateSerializer(new_form_template).data

    def update(self, instance, validated_data):
        pass


class DataSerializer(serializers.Serializer):

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UpdateSerializer(serializers.Serializer):
    querys = serializers.JSONField(
        label='查询参数对象', write_only=True
    )
    updated = serializers.IntegerField(read_only=True, label='更新成功数量')
    template_id = serializers.CharField(label='模板ID', write_only=True)

    update_fields = serializers.JSONField(write_only=True, label='更新字段对象')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class DeleteDataSerializer(serializers.Serializer):
    querys = serializers.JSONField(
        label='查询参数对象', write_only=True
    )
    deleted = serializers.ListField(
        child=serializers.CharField(), label='已删除PK数组', read_only=True
    )
    template_id = serializers.CharField(label='模板ID', write_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
