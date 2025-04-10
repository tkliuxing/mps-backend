import json
import logging
from typing import Type, Union
from collections import namedtuple

from django.core.exceptions import FieldDoesNotExist
from django.db import models as django_models
from django.db.models import Q, QuerySet
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import api_view, permission_classes
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CharField, HyperlinkedRelatedField
from rest_framework.utils.field_mapping import ClassLookupDict, get_field_kwargs, get_relation_kwargs
from rest_framework.exceptions import ParseError
from rest_framework.utils import model_meta
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import permissions, filters as sfilter
from rest_framework import serializers as rserial
from django.shortcuts import get_object_or_404

from usercenter.permissions import IsSuperuser
from utility.filter_fields import (CharInFilter, NumberInFilter)
from org.models import Org
from service.models import Services
from customer.models import Customer
from goods.models import Goods
from . import serializers
from . import models
from . import filters as self_filters
from . import tasks

logger = logging.getLogger('restapi')

TemplateModelType = Union[Type[models.FormData], Type[Org], Type[Services], Type[Customer], Type[Goods]]


class FormFieldsViewSet(ModelViewSet):
    """模版字段 formtemplate_formfields"""
    queryset = models.FormFields.objects.order_by('sort_num', 'pk')
    serializer_class = serializers.FormFieldsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('sys_id', 'org_id', 'biz_id', 'template',)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.sys_id = instance.template.sys_id
        instance.org_id = instance.template.org_id
        instance.biz_id = instance.template.biz_id
        instance.src_id = instance.template.src_id
        instance.save()
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.sys_id = instance.template.sys_id
        instance.biz_id = instance.template.biz_id
        instance.src_id = instance.template.src_id
        instance.save()
        return instance


class FormTemplateViewSet(ModelViewSet):
    """模板 formtemplate_formtemplate"""
    queryset = models.FormTemplate.objects.order_by('-create_time')
    serializer_class = serializers.FormTemplateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, sfilter.SearchFilter)
    filterset_class = self_filters.FormTemplateFilterSet
    search_fields = ('title', 'keyword', 'id',)

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        return qs.distinct()


class FormTemplateMinViewSet(ModelViewSet):
    """模板 formtemplate_formtemplate"""
    queryset = models.FormTemplate.objects.order_by('-create_time')
    serializer_class = serializers.FormTemplateMinSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, sfilter.SearchFilter)
    filterset_class = self_filters.FormTemplateFilterSet
    search_fields = ('keyword', 'id',)


class FormAggrgateFieldsViewSet(ModelViewSet):
    queryset = models.FormAggrgateFields.objects.order_by('pk')
    serializer_class = serializers.FormAggrgateFieldsSerializer
    permission_classes = [IsSuperuser]


class FormTemplateCodeViewSet(UpdateModelMixin, RetrieveModelMixin, GenericViewSet):
    """模板 formtemplate_formtemplate"""
    queryset = models.FormTemplate.objects.order_by('-create_time').only('pk', 'code')
    serializer_class = serializers.FormTemplateCodeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class FormDataReportConfViewSet(ModelViewSet):
    """表单数据报表 formtemplate_formdatareportconf"""
    queryset = models.FormDataReportConf.objects.order_by('sys_id', 'biz_id', 'report_id')
    serializer_class = serializers.FormDataReportConfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, sfilter.SearchFilter,)
    filterset_fields = ('sys_id', 'org_id', 'biz_id', 'report_id',)
    search_fields = ('report_name', 'report_id',)


class FormTemplateCopyViewSet(CreateModelMixin, GenericViewSet):
    """表单模板复制"""
    queryset = models.FormTemplate.objects.all()
    serializer_class = serializers.FormTemplateCopySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        表单模板复制

        通过源模板ID form_id 和目标系统ID target_id 复制一个新的模版到目标系统，返回新模版ID pk
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        return Response(data, status=201)

    def perform_create(self, serializer):
        return serializer.save()


def dictfetchall(sql, args=None):
    """Returns all rows from a cursor as a dict"""
    from django.db import connection
    with connection.cursor() as cursor:
        if args:
            cursor.execute(sql, tuple(args))
        else:
            cursor.execute(sql)
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))  # type: ignore
            for row in cursor.fetchall()
        ]


def listfetchall(sql, *args):
    """Returns all rows from a cursor as a dict"""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(sql, *args)
        desc = cursor.description
        headers = [col[0] for col in desc]  # type: ignore
        return headers, cursor.fetchall()


class FormDataReportView(APIView):
    """报表结果查询"""
    model = models.FormDataReportConf
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def parse_json(self, conf_text):
        return json.loads(conf_text)

    def sql_order_by_safe_check(self, field):
        raw_str = field.lower()
        bad_words = ['select', 'delete', 'update', 'drop', 'truncate', 'insert', 'create', 'alter', 'grant', 'revoke', ' ', ';']
        for word in bad_words:
            if word in raw_str:
                raise ValueError(f'非法SQL {field}')

    def parse_order_by(self, context):
        field_names = context.split(',')
        for field in field_names:
            self.sql_order_by_safe_check(field)
        fields = ', '.join([
            f'{i[1:]} DESC' if i.startswith('-') else f'{i} ASC'
            for i in field_names
        ])
        return f'ORDER BY {fields}'

    def get_sql_field_list(self, request, conf):
        field_list = []
        for field in conf:
            if field['field'] is None:
                continue
            query_name = field.get('query_name') or field['field']
            has_value = (field['field'] in request.GET and request.GET[field['field']]) or (
                'query_name' in field and field['query_name'] in request.GET and request.GET[field['query_name']])
            if field.get('required', False) and not has_value:
                raise ValidationError('{}是必须参数'.format(query_name))
            if not has_value and 'default' in field and field['default']:
                has_value = True
            if has_value:
                if 'exp' in field:
                    field_list.append(
                        (field['field'], field['exp'],)
                    )
                elif field['field'].lower() == 'order by':
                    field_list.append(self.parse_order_by(request.GET[field['query_name']]))
                else:
                    field_list.append(field['field'])
        return field_list

    def get_sql_value_list(self, request, conf):
        value_list = []
        for field in conf:
            if field['field'] is None:
                continue
            val = '._.--_._.'
            if field.get('exp', '').lower() in ['is null', 'is not null']:
                continue
            if field['field'].lower() == 'order by':
                continue
            if field['field'] in request.GET and request.GET[field['field']]:
                val = request.GET[field['field']]
            elif 'query_name' in field and field['query_name'] in request.GET and request.GET[field['query_name']]:
                val = request.GET[field['query_name']]
            elif 'default' in field and field['default']:
                val = field['default']
            if field.get('exp', '').lower() == 'in' and val != '._.--_._.':
                val = tuple(val.split(','))
            if val != '._.--_._.':
                value_list.append(val)
        return value_list

    def gen_where(self, params):
        def pare_ext(pp):
            if isinstance(pp, tuple):
                if pp[1].lower() in ['is null', 'is not null']:
                    return f"{pp[0]} {pp[1]}"
                return f"({pp[0]} {pp[1]} %s)"
            else:
                return f"{pp} = %s"
        return " AND ".join(
            map(
                pare_ext,
                params
            )
        )

    def gen_limit(self, params):
        seq = []
        for p in params:
            if isinstance(p, str) and p.startswith('ORDER BY'):
                seq.append(p)
            elif not isinstance(p, tuple):
                seq.append(f'{p} %s')
            else:
                seq.append(f'({p[0]} {p[1]} %s)')
        return " ".join(seq)

    def gen_sql(self, report):
        obj = report
        arguments_conf = self.parse_json(obj.arguments)
        if 'sql' not in arguments_conf:
            raise ValueError('配置错误')
        values = []
        params = []
        limit_params = []
        sql = arguments_conf.get('sql')
        fix_sql = sql.lower()
        if 'delete' in fix_sql or 'update' in fix_sql:
            raise ValueError('非法SQL')
        if arguments_conf.get('sql_params'):
            params = self.get_sql_field_list(self.request, arguments_conf.get('sql_params'))
            values = self.get_sql_value_list(self.request, arguments_conf.get('sql_params'))
        if arguments_conf.get('limit_params'):
            limit_params = self.get_sql_field_list(self.request, arguments_conf.get('limit_params'))
            values.extend(self.get_sql_value_list(self.request, arguments_conf.get('limit_params')))
        if params and limit_params:
            where_str = self.gen_where(params)
            limit_str = self.gen_limit(limit_params)
            try:
                sql = sql.format(" AND " + where_str, limit_str)
            except Exception as e:
                logger.error(f'format error: {sql}\n{where_str}\n{limit_str}', exc_info=e)
                raise e
        elif params:
            where_str = self.gen_where(params)
            sql = sql.format(" AND " + where_str)
        elif limit_params:
            limit_str = self.gen_limit(limit_params)
            if arguments_conf.get('sql_params'):
                sql = sql.format('', limit_str)
            else:
                sql = sql.format(limit_str)
        else:
            sql = sql.format("")
        logger.info(f"Report SQL {obj.report_id}: {sql}; WITH values {values}")
        return sql, values

    def get(self, request, *args, **kwargs):
        """
        报表结果查询

        需要在url中填写 report_id，如： /api/v1/formdatareport/3006/

        返回值结构：
        ```json
        {
            "id": "report_id"
            "title": "report_id"
            "data": [{"field1": "aaa", "field2": "vvv", "field3": "bbb", ...}, ...]
            "header": [{"key": "field1", "title": "姓名", "type": "str"}, ...]
            "charts": charts_conf_obj
        }
        ```
        """
        obj = get_object_or_404(self.model, report_id=kwargs['report_id'])
        data_struct_conf = self.parse_json(obj.data_struct)
        charts_struct_conf = self.parse_json(obj.charts_struct)
        result_dict = {}
        try:
            sql, values = self.gen_sql(obj)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        if values and values[0]:
            data = dictfetchall(sql, values)
        else:
            data = dictfetchall(sql)
        result_dict['id'] = kwargs['report_id']
        result_dict['title'] = obj.report_name
        result_dict['data'] = data
        header = data_struct_conf.get('header')
        if header is None and len(data) > 0:
            header = [{"key": x, "title": x, "type": 'str', "length": 30} for x in data[0].keys()]
        result_dict['header'] = header
        result_dict['charts'] = charts_struct_conf
        return Response(result_dict)

    def post(self, request, *args, **kwargs):
        self.request._request.GET = self.request.data.copy()  # type: ignore
        return self.get(self.request, *args, **kwargs)  # type: ignore


class FormDataReportCompressionView(FormDataReportView):
    """报表结果查询数据压缩"""
    model = models.FormDataReportConf
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        """
        报表结果查询数据压缩

        需要在url中填写 report_id，如： /api/v1/formdatareport/3006/

        返回值结构：
        ```json
        {
            "id": "report_id"
            "title": "report_id"
            "data": [[1,2,3], [2,3,4], ...]
            "header": [{"key": "A", "title": "aaa", "type": "str"}, ...]
            "charts": charts_conf_obj
        }
        ```
        """
        obj = get_object_or_404(self.model, report_id=kwargs['report_id'])
        data_struct_conf = self.parse_json(obj.data_struct)
        charts_struct_conf = self.parse_json(obj.charts_struct)
        result_dict = {}
        try:
            sql, values = self.gen_sql(obj)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        if values and values[0]:
            hd, data = listfetchall(sql, values)
        else:
            hd, data = listfetchall(sql)
        result_dict['id'] = kwargs['report_id']
        result_dict['title'] = obj.report_name
        result_dict['data'] = data
        header = data_struct_conf.get('header')
        if header is None and len(data) > 0:
            header = [{"key": x, "title": x, "type": 'str'} for x in hd]
        result_dict['header'] = header
        result_dict['charts'] = charts_struct_conf
        return Response(result_dict)

    def post(self, request, *args, **kwargs):
        self.request._request.GET = self.request.data.copy()
        return self.get(self.request, *args, **kwargs)


class FormDataReportTestView(APIView):
    """测试报表结果查询"""
    model = models.FormDataReportConf
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        测试报表结果查询

        返回值结构：
        ```json
        [
            {"字段名": "字段值"},
        ]
        ```
        """

        sql = request.data.get('sql')
        if not sql:
            return Response([])
        fix_sql = sql.lower()
        if 'delete' in fix_sql or 'update' in fix_sql:
            return Response({'title': "sql 非法"})
        try:
            return Response(dictfetchall(sql))
        except BaseException as e:
            return Response(str(e))


def get_serializer_class(
        model_class: TemplateModelType,
        template: models.FormTemplate,
        no_related=False, bulk=False
) -> Type[rserial.ModelSerializer]:

    class SerializerClass(rserial.ModelSerializer):
        class Meta:
            model = model_class
            fields = [
                'pk', 'sys_id', 'org_id'
            ]

        def validate(self, attrs):
            if bulk:
                return attrs
            org_id = attrs.get('org_id')
            if org_id is None:
                return attrs
            unique_fields = template.unique_fields
            if hasattr(self, 'instance') and self.instance is not None:
                pk = self.instance.pk
            else:
                pk = None
            if len(unique_fields) == 0:
                return attrs
            for f in unique_fields:
                val = attrs.get(f.col_name)
                if val is None:
                    continue
                qs = model_class.objects.filter(**{f.col_name: val, 'org_id': org_id, 'template_id': template.pk, 'sys_id': template.sys_id})
                if pk is not None:
                    qs = qs.exclude(pk=pk)
                if qs.exists():
                    raise ValidationError(f'{f.col_title}: {val} 数据已存在!')
            return attrs

        def create(self, validated_data):
            if hasattr(model_class, 'src_id') and not validated_data.get('src_id'):
                validated_data['src_id'] = int(validated_data.get('org_id', 0)) % 100
            data = super().create(validated_data)
            if hasattr(model_class, 'gps_sn') and not validated_data.get('gps_sn', None):
                data.gps_sn = str(data.id)
                data.save()
            return data

        def update(self, instance, validated_data):
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

    if hasattr(model_class, 'biz_id'):
        SerializerClass.Meta.fields.append("biz_id")
    if hasattr(model_class, 'src_id'):
        SerializerClass.Meta.fields.append("src_id")

    related_fields = template.related_fields
    no_related_fields = template.no_related_fields
    obj_id_field = template.obj_id_field
    info = model_meta.get_field_info(model_class)
    field_dicts = {}

    if template.has_rel_template and not no_related and obj_id_field and obj_id_field.related_template:
        related_template = obj_id_field.related_template  # type: models.FormTemplate
        rel_info = model_meta.get_field_info(related_template.get_model())
        for f in related_fields:
            # 根据模版字段配置的
            display_name = f.field_alias
            field_name = f.col_name
            if field_name in rel_info.fields_and_pk:
                model_field = rel_info.fields_and_pk[field_name]
                field_class, field_kwargs = get_serializer_type(field_name, model_field)
                field_kwargs['read_only'] = True
            else:
                continue
            field_dicts[display_name] = field_class(**field_kwargs)  # type: ignore
            SerializerClass._declared_fields[display_name] = field_dicts[display_name]  # type: ignore
            SerializerClass.Meta.fields.append(display_name)
    for f in no_related_fields:
        alias = f.field_alias
        field_name = f.col_name
        if field_name in info.fields_and_pk:
            model_field = info.fields_and_pk[field_name]
            field_class, field_kwargs = get_serializer_type(field_name, model_field)
        else:
            if field_name.endswith('_id'):
                fid = field_name[:-3]
            else:
                fid = field_name
            model_field = info.relations[fid]
            field_class, field_kwargs = build_relational_field(field_name, model_field)
        if f.col_name != alias:
            field_dicts[alias] = field_class(source=f.col_name, **field_kwargs)  # type: ignore
        else:
            field_dicts[alias] = field_class(**field_kwargs)  # type: ignore
        SerializerClass._declared_fields[alias] = field_dicts[alias]  # type: ignore
        SerializerClass.Meta.fields.append(alias)
    if template.api_name in ['goods', 'customer', 'org']:
        SerializerClass._declared_fields["gps_sn"] = rserial.CharField(  # type: ignore
            max_length=128, label='定位编码', allow_null=True, allow_blank=True,
            help_text='创建时传空字符串会自动生成SN', required=False
        )
        SerializerClass.Meta.fields.append("gps_sn") if 'gps_sn' not in SerializerClass.Meta.fields else None
    if hasattr(model_class, 'template_id') or hasattr(model_class, 'template'):
        SerializerClass._declared_fields["template_id"] = CharField()  # type: ignore
        SerializerClass.Meta.fields.append("template_id")
    instance_class = namedtuple(template.pk, SerializerClass.Meta.fields)
    SerializerClass.instance_class = instance_class
    SerializerClass.to_namedtuple = lambda self: self.instance_class(**self.data)
    return SerializerClass


def get_filtersetclass_and_searchfields(model_class: TemplateModelType, template: models.FormTemplate):
    import django_filters
    from django_filters.filterset import FILTER_FOR_DBFIELD_DEFAULTS
    mapper = dict(map(lambda x: (x[0], x[1]['filter_class']), FILTER_FOR_DBFIELD_DEFAULTS.items()))
    field_mapping = ClassLookupDict(mapper)

    fields = template.filter_fields
    info = model_meta.get_field_info(model_class)
    rel_model = template.rel_model
    rel_model_info = model_meta.get_field_info(rel_model) if rel_model else None
    search_fields = ['id']
    ordering_fields = [('create_time', 'create_time',)]
    meta_fields = ['sys_id', 'org_id', 'biz_id']
    if hasattr(model_class, 'biz_id'):
        meta_fields.append('biz_id')
    if hasattr(model_class, 'src_id'):
        meta_fields.append('src_id')

    class FilterSetClass(django_filters.FilterSet):
        id = CharInFilter(field_name='id')
        pk = CharInFilter(field_name='pk')
        department_in = CharInFilter(field_name='department_id') if hasattr(model_class, 'department_id') else None

        class Meta:
            model = model_class
            fields = meta_fields

        def include_gps(self, qs, name, value):
            return qs

    # FilterSetClass.base_filters['template_id'] = django_filters.CharFilter(field_name='template_id')

    for f in fields:
        alias = f.field_alias
        model_field = None
        if f.is_related:
            col_name = f'obj__{f.col_name}'
            model_field = rel_model_info.fields_and_pk[f.col_name] if rel_model_info and f.col_name in rel_model_info.fields_and_pk else None
        else:
            col_name = f.col_name
        if model_class == models.FormData and col_name in ['parent', 'user', 'department', ]:
            FilterSetClass.base_filters[alias] = CharInFilter(field_name=col_name)  # type: ignore
            continue
        if col_name in info.fields_and_pk:
            model_field = info.fields_and_pk[col_name]
        elif col_name in info.relations:
            if model_class != models.FormData:
                model_field = django_models.CharField(max_length=64)
        elif model_field is not None:
            pass
        else:
            continue
        if isinstance(model_field, django_models.DateTimeField):
            field_class = django_filters.DateTimeFromToRangeFilter
        elif isinstance(model_field, django_models.DateField):
            field_class = django_filters.DateFromToRangeFilter
        elif isinstance(model_field, django_models.CharField):
            field_class = CharInFilter
        elif isinstance(model_field, (
                django_models.IntegerField,
                django_models.FloatField,
                django_models.DecimalField
        )):
            field_class = NumberInFilter
        else:
            field_class = field_mapping[model_field]
        FilterSetClass.base_filters[alias] = field_class(field_name=col_name)  # type: ignore
        if not isinstance(model_field, django_models.ForeignKey) and \
                col_name != 'department' and \
                col_name != 'obj_id' and \
                col_name not in info.relations:
            search_fields.append(col_name)
        ordering_fields.append((col_name, alias,))
        if isinstance(model_field, (
                django_models.IntegerField,
                django_models.FloatField,
                django_models.DecimalField
        )):
            FilterSetClass.base_filters[alias + '_range'] = django_filters.RangeFilter(field_name=col_name)  # type: ignore
        if isinstance(model_field, django_models.CharField):
            FilterSetClass.base_filters[alias + '_like'] = django_filters.CharFilter(field_name=col_name, lookup_expr='contains')  # type: ignore
        FilterSetClass.base_filters[alias + '_isnull'] = django_filters.BooleanFilter(  # type: ignore
            field_name=col_name, lookup_expr='isnull'
        )
    if hasattr(model_class, 'gps_sn'):
        FilterSetClass.base_filters['include_gps'] = django_filters.BooleanFilter(method='include_gps')  # type: ignore
    if ordering_fields:
        FilterSetClass.base_filters['o'] = django_filters.OrderingFilter(fields=tuple(ordering_fields))  # type: ignore
    return FilterSetClass, search_fields


def get_serializer_type(field_name, model_field, digit_length=None):
    from rest_framework.fields import ModelField, ChoiceField, CharField
    mapper = ModelSerializer.serializer_field_mapping
    field_mapping = ClassLookupDict(mapper)
    try:
        field_class = field_mapping[model_field]
    except:
        field_class = None
    field_kwargs = get_field_kwargs(field_name, model_field)
    if model_field.one_to_one and model_field.primary_key:
        field_class = PrimaryKeyRelatedField
        field_kwargs['queryset'] = model_field.related_model.objects
    if 'choices' in field_kwargs:
        field_class = ChoiceField
        valid_kwargs = {
            'read_only', 'write_only',
            'required', 'default', 'initial', 'source',
            'label', 'help_text', 'style',
            'error_messages', 'validators', 'allow_null', 'allow_blank',
            'choices'
        }
        for key in list(field_kwargs):
            if key not in valid_kwargs:
                field_kwargs.pop(key)
    if not issubclass(field_class, ModelField):  # type: ignore
        field_kwargs.pop('model_field', None)
    if not issubclass(field_class, CharField) and not issubclass(field_class, ChoiceField):  # type: ignore
        field_kwargs.pop('allow_blank', None)
    return field_class, field_kwargs


def build_relational_field(field_name, relation_info):
    """
    Create fields for forward and reverse relationships.
    """
    field_class = ModelSerializer.serializer_related_field
    field_kwargs = get_relation_kwargs(field_name, relation_info)

    to_field = field_kwargs.pop('to_field', None)
    if to_field and not relation_info.reverse and not relation_info.related_model._meta.get_field(to_field).primary_key:
        field_kwargs['slug_field'] = to_field
        field_class = ModelSerializer.serializer_related_to_field

    # `view_name` is only valid for hyperlinked relationships.
    if not issubclass(field_class, HyperlinkedRelatedField):
        field_kwargs.pop('view_name', None)

    return field_class, field_kwargs


def get_update_serializer_class(model_class, template):
    slc = get_serializer_class(model_class, template, no_related=True, bulk=True)

    class UpdateSerializer(rserial.Serializer):
        querys = rserial.JSONField(
            label='查询参数对象', write_only=True
        )
        updated = rserial.IntegerField(read_only=True, label='更新成功数量')
        template_id = rserial.CharField(label='模板ID', write_only=True)

        update_fields = slc(write_only=True)

        def update(self, instance, validated_data):
            pass

        def create(self, validated_data):
            pass

    return UpdateSerializer


def get_create_serializer_class(model_class, template: models.FormTemplate):
    class SerializerClass(rserial.ModelSerializer):
        class Meta:
            model = model_class
            fields = [
                'pk', 'sys_id', 'org_id'
            ]

        def validate(self, attrs):
            org_id = attrs.get('org_id')
            if org_id is None:
                return attrs
            unique_fields = template.unique_fields
            if len(unique_fields) == 0:
                return attrs
            for f in unique_fields:
                val = attrs.get(f.col_name)
                if val is None:
                    continue
                exists = model_class.objects.filter(**{f.col_name: val, 'org_id': org_id, 'template_id': template.pk, 'sys_id': template.sys_id}).exists()
                if exists:
                    raise ValidationError(f'{f.col_title}: {val} 数据已存在!')
            return attrs

        def create(self, validated_data):
            if hasattr(model_class, 'src_id') and not validated_data.get('src_id'):
                validated_data['src_id'] = int(validated_data.get('org_id', 0)) % 100
            data = super().create(validated_data)
            if hasattr(model_class, 'gps_sn') and not validated_data.get('gps_sn', None):
                data.gps_sn = str(data.id)
                data.save()
            return data

        def update(self, instance, validated_data):
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

    if hasattr(model_class, 'biz_id'):
        SerializerClass.Meta.fields.append("biz_id")
    if hasattr(model_class, 'src_id'):
        SerializerClass.Meta.fields.append("src_id")

    no_related_fields = template.no_related_fields
    info = model_meta.get_field_info(model_class)
    field_dicts = {}

    for f in no_related_fields:
        alias = f.field_alias
        field_name = f.col_name
        if field_name in info.fields_and_pk:
            model_field = info.fields_and_pk[field_name]
            field_class, field_kwargs = get_serializer_type(field_name, model_field)
        else:
            if field_name.endswith('_id'):
                fid = field_name[:-3]
            else:
                fid = field_name
            model_field = info.relations[fid]
            field_class, field_kwargs = build_relational_field(field_name, model_field)
        if f.col_name != alias:
            field_dicts[alias] = field_class(source=f.col_name, **field_kwargs)  # type: ignore
        else:
            field_dicts[alias] = field_class(**field_kwargs)  # type: ignore
        SerializerClass._declared_fields[alias] = field_dicts[alias]  # type: ignore
        SerializerClass.Meta.fields.append(alias)
    if template.api_name in ['goods', 'customer', 'org']:
        SerializerClass._declared_fields["gps_sn"] = rserial.CharField(  # type: ignore
            max_length=128, label='定位编码', allow_null=True, allow_blank=True,
            help_text='创建时传空字符串会自动生成SN', required=False
        )
        SerializerClass.Meta.fields.append("gps_sn") if 'gps_sn' not in SerializerClass.Meta.fields else None
    if hasattr(model_class, 'template_id') or hasattr(model_class, 'template'):
        SerializerClass._declared_fields["template_id"] = CharField()  # type: ignore
        SerializerClass.Meta.fields.append("template_id")
    return SerializerClass


class DataBulkDeleteView(GenericViewSet):
    """通用数据批量删除接口"""
    queryset = models.FormTemplate.objects.none()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = serializers.DeleteDataSerializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.template_id = None
        self.sys_id = None
        method = request.method.lower()
        if method in ['get', 'delete', 'options']:
            self.template_id = request.GET.get('template_id')
            self.sys_id = request.GET.get('sys_id')
        if method in ['post', 'put', 'patch']:
            self.template_id = request.data.get('template_id')
            self.sys_id = request.data.get('sys_id')
        if self.sys_id is None:
            logger.warning('DataBulkDeleteView Bad sys_id')
            raise ValidationError('Bad sys_id')
        # initial template
        if self.template_id:
            try:
                self.template = models.FormTemplate.get_by_id(self.template_id)
            except models.FormTemplate.DoesNotExist:
                raise ParseError('Bad template_id')
            if self.template.need_login and (not request.user or not request.user.is_authenticated):
                raise ParseError('403 Forbidden')
            self.initial_model()
            self.initial_filter()
        else:
            logger.warning('DataBulkDeleteView Bad template_id')
            raise ParseError('Bad sys_id')

    def initial_model(self):
        self.model = self.template.get_model()
        self.queryset = self.model.objects.filter(template=self.template).order_by('-create_time')
        if self.template.api_name == 'formdata':
            if self.request.method == 'GET':
                src_id = self.request.GET.get('src_id')
                org_id = self.request.GET.get('org_id')
            else:
                src_id = self.request.data.get('src_id')  # type: ignore
                org_id = self.request.data.get('org_id')  # type: ignore
            if org_id and not src_id:
                self.queryset = self.queryset.filter(src_id=int(org_id) % 100)
            if src_id:
                self.queryset = self.queryset.filter(src_id=int(src_id) % 100)

    def initial_filter(self):
        self.filterset_class, self.search_fields = get_filtersetclass_and_searchfields(self.model, self.template)

    def create(self, request, *args, **kwargs):
        """
        通用数据接口：批量删除

        通过post数据批量删除模版对应的数据，必填模板ID

        例如以下JSON会删除 模版 "D129347t97" 对应数据中 `id` 在 "123948,01324h908,qs908ry123" 中，并且 `name` 等于 "abc" 的数据:

        ```json
        {
            "querys": {"id": "123948,01324h908,qs908ry123", "name": "abc"},
            "template_id": "D129347t97"
        }
        ```

        返回删除数据的pk数组:

        ```json
        {
            "deleted": ["123948", "01324h908"]
        }
        ```
        """
        from service.models import Services
        from org.models import Org
        from customer.models import Customer
        from goods.models import Goods
        serializer = self.get_serializer(data=request.data)  # type: serializers.DeleteDataSerializer
        pks = []
        serializer.is_valid(raise_exception=True)
        querys = serializer.validated_data['querys']
        template_id = serializer.validated_data['template_id']
        qs = self.model.objects.filter(template_id=template_id, sys_id=self.sys_id)
        ct1 = qs.count()
        qs = self.filterset_class(querys, qs).qs
        ct2 = qs.count()
        if ct1 == ct2 and ct1 > 1:
            raise ParseError('Not allowed to delete all data')
        pks = list(qs.values_list('id', flat=True))
        self.delete_log(pks)
        qs.delete()
        rel_objs = models.FormFields.objects.filter(related_template_id=template_id, col_name='obj_id').values('template_id').distinct()
        if rel_objs:
            models.FormData.objects.filter(template_id__in=rel_objs, obj_id__in=pks).update(obj_id=None)
            Services.objects.filter(template_id__in=rel_objs, obj_id__in=pks).update(obj_id=None)
            Org.objects.filter(template_id__in=rel_objs, obj_id__in=pks).update(obj_id=None)
            Customer.objects.filter(template_id__in=rel_objs, obj_id__in=pks).update(obj_id=None)
            Goods.objects.filter(template_id__in=rel_objs, obj_id__in=pks).update(obj_id=None)
        return Response({'deleted': pks})

    def delete_log(self, querys):
        if not querys:
            return
        from system.models import SystemLog
        from utility.client_ip import get_client_ip
        data = querys
        if self.request.user.is_anonymous:
            user = None
            user_name = get_client_ip(self.request)
            org_id = self.template.org_id
        else:
            user = self.request.user
            user_name = self.request.user.username
            org_id = self.request.user.org_id
        log = SystemLog.objects.create(
            sys_id=self.template.sys_id,
            org_id=org_id,
            log_level=0,
            log_type='删除',
            template_id=self.template.pk,
            user=user,
            user_name=user_name,
            content='DELETE:' + str(data),
        )
        print('log', log)


class DataBulkUpdateView(GenericViewSet):
    """通用数据批量更新接口"""
    queryset = models.FormTemplate.objects.none()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = serializers.UpdateSerializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.template_id = None
        method = request.method.lower()
        if method in ['get', 'delete', 'options']:
            self.template_id = request.GET.get('template_id')
        if method in ['post', 'put', 'patch']:
            self.template_id = request.data.get('template_id')
        # initial template
        if self.template_id:
            try:
                self.template = models.FormTemplate.get_by_id(self.template_id)
            except models.FormTemplate.DoesNotExist:
                raise ParseError('Bad template_id')
            self.initial_model()
            self.initial_filter()
            self.serializer_class = get_update_serializer_class(self.model, self.template)
        else:
            raise ParseError('DataBulkDeleteView Bad template_id')

    def initial_filter(self):
        self.filterset_class, self.search_fields = get_filtersetclass_and_searchfields(self.model, self.template)

    def initial_model(self):
        self.model = self.template.get_model()
        self.queryset = self.model.objects.filter(template=self.template).order_by('-create_time')
        if self.template.api_name == 'formdata':
            if self.request.method == 'GET':
                src_id = self.request.GET.get('src_id')
                org_id = self.request.GET.get('org_id')
            else:
                src_id = self.request.data.get('src_id')
                org_id = self.request.data.get('org_id')
            if org_id and not src_id:
                self.queryset = self.queryset.filter(src_id=int(org_id) % 100)
            if src_id:
                self.queryset = self.queryset.filter(src_id=int(src_id) % 100)

    def create(self, request, *args, **kwargs):
        """
        通用数据接口：批量更新

        通过post数据批量更新模版对应的数据的对应字段，必填模板ID 和 更新字段对象

        例如以下JSON会更新 模版 "D129347t97" 对应数据中 `id` 在 "123948,01324h908,qs908ry123" 中，并且 `name` 等于 "abc" 的数据
        , 设置字段 `age` 为 20:

        ```json
        {
            "querys": {"id": "123948,01324h908,qs908ry123", "name": "abc"},
            "template_id": "D129347t97",
            "update_fields": {"age": 20}
        }
        ```

        返回更新数据的pk数组:

        ```json
        {
            "updated": 1
        }
        ```
        """
        slc = self.get_serializer_class()
        req_data = request.data
        if not req_data.get('update_fields'):
            return Response({'updated': 0})
        req_data['update_fields']['template_id'] = self.template_id
        serializer = slc(data=req_data)
        serializer.is_valid(raise_exception=True)
        querys = serializer.validated_data['querys']
        qs = self.model.objects.filter(template_id=self.template_id)
        qs = self.filterset_class(querys, qs).qs
        update = serializer.validated_data['update_fields']  # type: dict
        update['template_id'] = self.template_id
        update.pop('org_id', None)
        update.pop('src_id', None)
        update.pop('sys_id', None)
        update.pop('pk', None)
        count = qs.update(**update)
        self.update_log(querys)
        return Response({'updated': count})

    def update_log(self, querys):
        if not querys:
            return
        from system.models import SystemLog
        from utility.client_ip import get_client_ip
        data = querys
        if self.request.user.is_anonymous:
            user = None
            user_name = get_client_ip(self.request)
            org_id = self.template.org_id
        else:
            user = self.request.user
            user_name = self.request.user.username
            org_id = self.request.user.org_id
        log = SystemLog.objects.create(
            sys_id=self.template.sys_id,
            org_id=org_id,
            log_level=0,
            log_type='编辑',
            template_id=self.template.pk,
            user=user,
            user_name=user_name,
            content='UPDATE :' + str(data),
        )
        print('log', log)


class DataViewSet(ModelViewSet):
    """通用数据CURD接口, 必须具有 template_id (formtemplate_formtemplate.id)"""
    queryset = models.FormTemplate.objects.none()
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.DataSerializer
    filter_backends = (DjangoFilterBackend, sfilter.SearchFilter,)
    filterset_class = None
    search_fields = ('sys_id',)

    def create(self, request, *args, **kwargs):
        """
        通用数据接口：新增

        传对象新增一个：
        ```json
        {
            "template_id": "D129347t97",
            "name": "abc",
            "age": 20
        }
        ```

        传数组新增多个, 必须为同一 "template_id" 的数据：
        ```json
        [
            {
                "template_id": "D129347t97",
                "name": "abc",
                "age": 20
            },
            {
                "template_id": "D129347t97",
                "name": "def",
                "age": 25
            }
        ]
        ```

        返回值结构由模板配置决定
        """
        try:
            sys_id = request.data.get('sys_id') if isinstance(request.data, dict) else request.data[0].get('sys_id')
        except IndexError:
            raise ParseError('Data is empty!')
        if str(sys_id) != str(self.template.sys_id):
            raise ParseError('sys_id error!')
        serializer_class = get_create_serializer_class(self.template.get_model(), self.template)
        if isinstance(request.data, list):
            serializer = serializer_class(data=request.data, many=True)
        else:
            serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        data = serializer.save()
        if isinstance(data, list):
            for i in data:
                self.fetl_post_data(self.template_id, i.pk)
            return
        data.save()
        self.fetl_post_data(self.template_id, data.pk)
        # model_id_prefix = get_model_id_prefix(self.model)
        # if hasattr(serializer, 'many') and serializer.many is True:
        #     for index, attrs in enumerate(serializer.validated_data):
        #         attrs['id'] = gen_new_id(model_id_prefix, index)
        #         serializer.child.create(attrs)
        # else:
        #     super().perform_create(serializer)

    def update(self, request, *args, **kwargs):
        """
        通用数据接口：单条更新

        返回值结构由模板配置决定
        """
        sys_id = request.data.get('sys_id')
        if str(sys_id) != str(self.template.sys_id):
            raise ParseError('sys_id error!')
        return super().update(request, *args, **kwargs)

    def get_from_cache(self):
        cache_key = self.request.get_full_path()
        return cache.get(cache_key)

    def list(self, request, *args, **kwargs):
        """
        通用数据接口：查询

        必须在get的query中传: `sys_id`, `template_id`

        其他查询参数由模板配置指定；当配置 `是否为过滤条件` 为 "是" 的时候才会包含该字段为过滤条件

        任意字段可查询是否为空：
        `name_isnull=true` 即为查询 "name" 为空的数据,
        `name_isnull=false` 即为查询 "name" 不为空的数据

        任意 `字符串类型`, `数值类型` 的字段过滤条件值均可为多个，用逗号隔开：
        `name=abc,def,ghi` 即为查询 "name" 在 "abc,def,ghi" 中的数据

        任意 `日期类型`, `时间类型` 的字段过滤条件均可是范围查询：
        `create_time_after=2021-01-01&create_time_before=2020-12-31`
        即为查询 "create_time" 在 `2021-01-01 至 2020-12-31` 范围内的数据

        任意 `数值类型`的字段过滤条件均可是范围查询：
        `float_01_range_min=1&float_01_range_max=20`
        即为查询 "float_01" 在 `1 至 20`范围内的数据

        按照部门查询：
        `department_in=由逗号分隔的部门ID字符串`
        一般用于区分数据权限，使用myinfo接口获取的当前用户的department_child_ids进行查询。
        如：当前用户的 `myinfo.data_permission` 是 `本部门` 时增加query参数 `department_in:myinfo.department_child_ids`

        查询返回值结构由模板配置决定；
        如果是物表数据，可传 include_gps=true 来返回包含定位点信息的数据，"gps_point"： Point(定位信息结构数据)
        """
        cache_key = self.request.get_full_path()
        if request.query_params.get('use_cache'):
            data = self.get_from_cache()
            if data:
                return Response(data)
        from gps.utils import get_point_data
        sys_id = request.GET.get('sys_id')
        template = self.template
        if str(sys_id) != str(self.template.sys_id):
            raise ParseError('sys_id error!')
        queryset = self.filter_queryset(self.get_queryset())  # type: models.models.QuerySet
        # logger.debug(f"data queryset is: {queryset.query}")
        include_gps = request.GET.get('include_gps')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            if include_gps and (template.api_name in ['goods', 'customer', 'org']):
                data = [{'gps_point': get_point_data(i['gps_sn'], sys_id), **i} for i in data]
            resp = self.get_paginated_response(data)
            if request.query_params.get('use_cache'):
                cache.set(cache_key, resp.data, 1 * 60 * 60)
            return resp

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        if include_gps and (template.api_name in ['goods', 'customer', 'org']):
            ll = []
            for i in data:
                ll.append({'gps_point': get_point_data(i['gps_sn'], sys_id), **i})
            if request.query_params.get('use_cache'):
                cache.set(cache_key, ll, 1 * 60 * 60)
            return Response(ll)
        if request.query_params.get('use_cache'):
            cache.set(cache_key, data, 1 * 60 * 60)
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        """
        通用数据接口：单条删除

        无返回值结构
        """
        from service.models import Services
        from org.models import Org
        from customer.models import Customer
        from goods.models import Goods
        sys_id = request.GET.get('sys_id')
        if str(sys_id) != str(self.template.sys_id):
            raise ParseError('sys_id error!')
        self.model = self.template.get_model()
        self.queryset = self.model.objects.filter(template=self.template).order_by('-create_time')
        obj = self.queryset.filter(pk=self.kwargs['pk'])
        self.delete_log(obj)
        obj.delete()
        tasks.related_delete.delay(self.template_id, self.kwargs['pk'])
        return Response(status=204)

    def retrieve(self, request, *args, **kwargs):
        """
        通用数据接口：单条读取

        返回值结构由模板配置决定
        """
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        try:
            before_data = self.get_serializer(instance=self.get_object()).data
            after_data = dict(serializer.validated_data)
            self.update_log(before_data, after_data)
        except:
            pass
        data = serializer.save()
        self.fetl_post_data(self.template_id, data.pk)

    def partial_update(self, request, *args, **kwargs):
        """
        通用数据接口：单条部分更新

        返回值结构由模板配置决定
        """
        return super().partial_update(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.template_id = None
        method = request.method.lower()
        if method in ['get', 'delete', 'options']:
            self.template_id = request.GET.get('template_id')
        if method in ['post', 'put', 'patch']:
            if isinstance(request.data, list):
                if len(request.data) == 0:
                    raise ParseError('Data is empty!')
                self.template_id = request.data[0].get('template_id')
            else:
                self.template_id = request.data.get('template_id')
        # initial template
        if self.template_id:
            try:
                self.template = models.FormTemplate.get_by_id(self.template_id)
            except models.FormTemplate.DoesNotExist:
                raise ParseError('Bad template_id')
        else:
            raise ParseError('Bad template_id')
        if self.template.need_login and (not request.user or not request.user.is_authenticated):
            raise ParseError('403 Forbidden')
        self.initial_model()
        self.initial_serializer_class()
        self.initial_filter()

    def initial_model(self):
        if self.template.has_rel_template:
            self.model = self.template.get_related_model()
            annotate_dict = self.template.get_annotate_dict()
            self.queryset = self.model.objects.filter(template=self.template).annotate(
                **annotate_dict
            ).order_by('-create_time')
        else:
            self.model = self.template.get_model()
            self.queryset = self.model.objects.filter(template=self.template).order_by('-create_time')

    def initial_serializer_class(self):
        # serializer_pickle = cache.get(str(self.template_id))
        # if serializer_pickle:
        #     serializer_class = pickle.loads(serializer_pickle)
        # else:
        #     serializer_class = get_serializer_class(self.model, self.template)
        #     cache.set(str(self.template_id), pickle.dumps(serializer_class), 30)
        # self.serializer_class = serializer_class
        self.serializer_class = get_serializer_class(self.model, self.template)

    def initial_filter(self):
        self.filterset_class, self.search_fields = get_filtersetclass_and_searchfields(self.model, self.template)

    def delete_log(self, obj):
        if not obj:
            return
        if isinstance(obj, QuerySet):
            obj = obj.first()
        from system.models import SystemLog
        from utility.client_ip import get_client_ip
        serializer = self.get_serializer(obj)
        data = serializer.data
        if self.request.user.is_anonymous:
            user = None
            user_name = get_client_ip(self.request)
            org_id = obj.org_id or self.template.org_id
        else:
            user = self.request.user
            user_name = self.request.user.username
            org_id = self.request.user.org_id
        log = SystemLog.objects.create(
            sys_id=self.template.sys_id,
            org_id=org_id,
            log_level=0,
            log_type='删除',
            template_id=self.template.pk,
            user=user,
            user_name=user_name,
            content='DELETE:' + str(data),
        )
        print('log', log)

    def update_log(self, before, after):
        from system.models import SystemLog
        from utility.client_ip import get_client_ip
        pk = before.get('pk')
        data = f'{before} TO {after}'
        if self.request.user.is_anonymous:
            user = None
            user_name = get_client_ip(self.request)
            org_id = before.get('org_id', self.template.org_id)
        else:
            user = self.request.user
            user_name = self.request.user.username
            org_id = self.request.user.org_id
        SystemLog.objects.create(
            sys_id=self.template.sys_id,
            org_id=org_id,
            log_level=0,
            log_type='编辑',
            template_id=self.template.pk,
            user=user,
            user_name=user_name,
            content=f'UPDATE {self.template_id}: {pk}: {data}',
        )

    @staticmethod
    def fetl_post_data(template_id, date_id):
        try:
            from fetl.tasks import fetl_push_data
        except ImportError as e:
            logger.error(f'fetl_post_data error: {e}', exc_info=e)
            return
        try:
            fetl_push_data.delay(template_id, date_id)
        except Exception as e:
            logger.error(f'fetl_post_data error: {e}', exc_info=e)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def data_delete_one(request):
    from system.models import SystemLog
    from utility.client_ip import get_client_ip
    from .models import FormTemplate
    template_id = request.data.get('template_id')
    pk = request.data.get('pk')
    user = request.user
    if not template_id or not pk:
        raise ParseError('template_id and pk are required')
    template = FormTemplate.objects.get(id=template_id)
    model = template.get_model()
    obj = model.objects.get(pk=pk)
    serializer_class = get_serializer_class(model, template)
    serializer = serializer_class(obj)
    data = serializer.data
    user_name = get_client_ip(request)
    org_id = obj.org_id or template.org_id
    SystemLog.objects.create(
        sys_id=template.sys_id,
        org_id=org_id,
        log_level=0,
        log_type='删除',
        template_id=template.pk,
        user=user,
        user_name=user_name,
        content=f'DELETE {template_id}: {pk}: {data}',
    )
    obj.delete()
    return Response(status=204)


class DataFindViewSet(DataViewSet):
    def create(self, request, *args, **kwargs):
        """
        通用数据接口：查询

        必须在get的query中传: `sys_id`, `template_id`

        其他查询参数由模板配置指定；当配置 `是否为过滤条件` 为 "是" 的时候才会包含该字段为过滤条件

        任意字段可查询是否为空：
        `name_isnull=true` 即为查询 "name" 为空的数据,
        `name_isnull=false` 即为查询 "name" 不为空的数据

        任意 `字符串类型`, `数值类型` 的字段过滤条件值均可为多个，用逗号隔开：
        `name=abc,def,ghi` 即为查询 "name" 在 "abc,def,ghi" 中的数据

        任意 `日期类型`, `时间类型` 的字段过滤条件均可是范围查询：
        `create_time_after=2021-01-01&create_time_before=2020-12-31`
        即为查询 "create_time" 在 `2021-01-01 至 2020-12-31` 范围内的数据

        查询返回值结构由模板配置决定；
        如果是物表数据，可传 include_gps=true 来返回包含定位点信息的数据，"gps_point"： Point(定位信息结构数据)
        """
        self.request._request.GET = self.request.data.copy()
        return super().list(request, *args, **kwargs)


class DataFieldViewSet(ReadOnlyModelViewSet):
    """通用数据部分字段查询接口, 必须具有 template_id (formtemplate_formtemplate.id)"""
    queryset = models.FormTemplate.objects.none()
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.DataSerializer
    filter_backends = (DjangoFilterBackend, sfilter.SearchFilter,)
    filterset_class = None
    search_fields = ('sys_id',)

    def list(self, request, *args, **kwargs):
        """
        通用数据部分字段查询接口,不分页

        必须在get的query中传: `sys_id`, `template_id`, `field_names`

        `field_names` 可为多个，用逗号隔开：`field_names=abc,def,ghi`

        接口无默认排序，如需指定排序，则需要传入 `ordering` 参数，为用逗号分隔的排序条件如 `ordering=fname1,-fname2`

        接口默认按照字段值去重，如无需去重，则需要传入 `distinct=false`

        接口默认去除空值，任意查询字段为空的均不显示，如无需去除，则需要传入 `nullable=true`

        """
        from gps.utils import get_point_data
        sys_id = request.GET.get('sys_id')
        template = self.template
        if str(sys_id) != str(template.sys_id):
            raise ParseError('sys_id error!')
        include_gps = request.GET.get('include_gps')
        has_gps = include_gps and (template.api_name in ['goods', 'customer', 'org'])
        queryset = self.filter_queryset(self.get_queryset())
        F = django_models.F
        field_alias = {
            i.field_alias: F(i.col_name)
            for i in template.no_related_fields
            if i.field_alias in self.field_names and i.field_alias != i.col_name
        }
        if has_gps:
            self.field_names.append('gps_sn')
        if field_alias:
            queryset = queryset.order_by().annotate(**field_alias).values(*self.field_names)
        else:
            queryset = queryset.order_by().values(*self.field_names)
        nullable = request.GET.get('nullable')
        if nullable != 'true':
            qs_dict = {}
            for field in self.field_names:
                qs_dict[field + '__isnull'] = False
            queryset = queryset.filter(**qs_dict)
        distinct = request.GET.get('distinct')
        if not distinct == 'false':
            queryset = queryset.distinct()
        ordering = request.GET.get('ordering')
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))
        # logger.debug(f"data queryset is: {queryset.query}")
        data = []
        page = self.paginate_queryset(queryset)

        if page is not None:
            for i in page:
                if has_gps:
                    data.append({'gps_point': get_point_data(i['gps_sn'], sys_id), **dict(i)})
                else:
                    data.append(dict(i))
            return self.get_paginated_response(data)
        for i in queryset:
            if has_gps:
                data.append({'gps_point': get_point_data(i['gps_sn'], sys_id), **dict(i)})
            else:
                data.append(dict(i))
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """
        通用数据接口：单条读取

        返回值结构由模板配置决定
        """
        return Response(status=404)

    def create(self, request, *args, **kwargs):
        """
        通用数据部分字段查询接口,不分页

        必须在post的json中传: `sys_id`, `template_id`, `field_names`

        `field_names` 可为多个，用逗号隔开：`field_names=abc,def,ghi`

        接口无默认排序，如需指定排序，则需要传入 `ordering` 参数，为用逗号分隔的排序条件如 `ordering=fname1,-fname2`

        接口默认按照字段值去重，如无需去重，则需要传入 `distinct=false`

        接口默认去除空值，任意查询字段为空的均不显示，如无需去除，则需要传入 `nullable=true`

        """
        self.request._request.GET = self.request.data.copy()  # type: ignore
        return self.list(request, *args, **kwargs)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.template_id = None
        method = request.method.lower()
        if method in ['get', 'delete', 'options']:
            self.template_id = request.GET.get('template_id')
        if method in ['post', 'put', 'patch']:
            if isinstance(request.data, list):
                if len(request.data) == 0:
                    raise ParseError('Data is empty!')
                self.template_id = request.data[0].get('template_id')
            else:
                self.template_id = request.data.get('template_id')
        # initial template
        if self.template_id:
            try:
                self.template = models.FormTemplate.get_by_id(self.template_id)
            except models.FormTemplate.DoesNotExist:
                raise ParseError('Bad template_id')
        else:
            raise ParseError('Bad template_id')
        if self.template.need_login and (not request.user or not request.user.is_authenticated):
            raise ParseError('403 Forbidden')
        if method in ['get', 'options']:
            self.field_names = request.GET.get('field_names')
        else:
            self.field_names = request.data.get('field_names')  # type: ignore
        if self.field_names is None:
            raise ParseError('Require field_names!')
        self.field_names = self.field_names.split(',')
        all_alias = list(self.template.all_alias_names)
        valid_field_names = ['id', 'pk', 'create_time', 'obj_id'] + all_alias
        for field_name in self.field_names:
            if field_name not in valid_field_names:
                raise ParseError(f'Bad field_names: {field_name} not in {valid_field_names}!')
        ordering = request.GET.get('ordering')
        if ordering:
            order = [i.replace('-', '') for i in ordering.split(',')]
            for o in order:
                if o not in self.field_names:
                    raise ParseError(f'Bad ordering: {o} not in field_names!')
        self.initial_model()
        self.initial_filter()

    def initial_model(self):
        if self.template.has_rel_template:
            self.model = self.template.get_related_model()
            annotate_dict = self.template.get_annotate_dict()
            self.queryset = self.model.objects.filter(template=self.template).annotate(
                **annotate_dict
            ).order_by('-create_time')
        else:
            self.model = self.template.get_model()
            self.queryset = self.model.objects.filter(template=self.template).order_by('-create_time')

    def initial_filter(self):
        self.filterset_class, self.search_fields = get_filtersetclass_and_searchfields(self.model, self.template)


class DataAggregateViewSet(DataViewSet):
    http_method_names = ['get', 'post']

    def list(self, request, *args, **kwargs):
        from django.db.models import Count, Max, Min, Avg, Sum
        sys_id = request.GET.get('sys_id')
        if str(sys_id) != str(self.template.sys_id):
            raise ParseError('sys_id error!')
        queryset = self.filter_queryset(self.get_queryset())  # type: models.models.QuerySet
        aggregate_fields = self.template.aggregate_fields.all()
        if not aggregate_fields:
            return Response({})
        data = {}
        aggregate_params = {}
        for field in aggregate_fields:  # type: models.FormAggrgateFields
            if field.aggr_type == 'count':
                ct_dict = queryset.values(field.field.col_name).annotate(**{
                    f'ct_{field.aggr_name}': Count(field.field.col_name, distinct=True)
                }).aggregate(**{
                    field.aggr_name: Count(field.field.col_name)
                })
                data.update(ct_dict)
            elif field.aggr_type == 'max':
                aggregate_params[field.aggr_name] = Max(field.field.col_name)
            elif field.aggr_type == 'min':
                aggregate_params[field.aggr_name] = Min(field.field.col_name)
            elif field.aggr_type == 'avg':
                aggregate_params[field.aggr_name] = Avg(field.field.col_name)
            elif field.aggr_type == 'sum':
                aggregate_params[field.aggr_name] = Sum(field.field.col_name)
        data.update(queryset.aggregate(**aggregate_params))
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        return Response(status=404)

    def create(self, request, *args, **kwargs):
        self.request._request.GET = self.request.data.copy()
        return self.list(self.request, *args, **kwargs)
