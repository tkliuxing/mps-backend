import json
import csv
import io
from typing import List, Dict, Any, Optional, Type
from django.db.models import ForeignKey, DO_NOTHING, Model
from django.db.models.base import ModelBase
from baseconfig.models import BaseTree, copy_tree_node
from system.models import SystemOrg
from .const import M2M_MODELS_CHOICES

from .models import FormTemplate, FormFields, ManyToManyData


def copy_base_tree_with_params(params: Dict[str, Any], old_sys_id: int, new_sys_id: int) -> Dict[str, any]:
    if 'parent' in params and params['parent'].startswith('bt'):
        parent_node = BaseTree.objects.filter(sys_id=old_sys_id, pk=params['parent']).first()
        if not parent_node:
            return params
        new_node = BaseTree.objects.filter(sys_id=new_sys_id, name=parent_node.name, level=parent_node.level).first()
        if new_node:
            params['parent'] = new_node.pk
            return params
        else:
            new_node = copy_tree_node(parent_node, new_sys_id, 0, 1, 1)
            print(f'copy base tree node: {parent_node.name}')
            params['parent'] = new_node.pk
            return params
    elif 'parent_name' in params:
        if params.get('org_id') == 0:
            parent_node = BaseTree.objects.filter(sys_id=old_sys_id, name=params['parent_name'], org_id=0, level=0).first()
            if not parent_node:
                return params
            new_node = BaseTree.objects.filter(sys_id=new_sys_id, name=parent_node.name, level=0, org_id=0).first()
            if new_node:
                return params
            else:
                new_node = copy_tree_node(parent_node, new_sys_id, 0, 1, 1)
                print(f'copy base tree node: {parent_node.name}')
                return params
        else:
            parent_node = BaseTree.objects.filter(sys_id=old_sys_id, name=params['parent_name'], org_id=params.get('org_id'), level=0).first()
            if not parent_node:
                return params
            orgs = SystemOrg.objects.filter(sys_id=new_sys_id).values_list('org_id', flat=True)
            for org_id in orgs:
                new_node = BaseTree.objects.filter(sys_id=new_sys_id, name=parent_node.name, level=0, org_id=org_id).first()
                if new_node:
                    continue
                else:
                    new_node = copy_tree_node(parent_node, new_sys_id, org_id, 1, 1)
                    print(f'copy base tree node: {parent_node.name}')
                    params['org_id'] = org_id
            return params
    else:
        return params


def copy_field_data_source(form_field, old_sys_id):
    if not form_field.local_data_source:
        return
    try:
        data = json.loads(form_field.local_data_source)
    except json.JSONDecodeError:
        return
    if not isinstance(data, dict):
        return
    url = data.get('url')
    if not url:
        return
    params = data.get('params')
    if not params:
        return
    new_sys_id = form_field.template.sys_id
    if url not in ('basetree', 'data', 'data-field-list'):
        return
    if url == 'basetree':
        data['params'] = copy_base_tree_with_params(params, old_sys_id, new_sys_id)
        form_field.local_data_source = json.dumps(data, ensure_ascii=False, indent=2)
    if url == 'data' or url == 'data-field-list':
        if 'template_id' not in params:
            return
        new_template = copy_template(params['template_id'], new_sys_id)
        print(f'copy form template: {params["template_id"]}')
        params['template_id'] = new_template.pk
        data['params'] = params
        form_field.local_data_source = json.dumps(data, ensure_ascii=False, indent=2)


def copy_field(old_form_template, new_form_template):
    form_fields = FormFields.objects.filter(template_id=old_form_template.pk)
    form_fields_bulk = []
    for i, field in enumerate(form_fields):
        field.pk = None
        field.template = new_form_template
        copy_field_data_source(field, old_form_template.sys_id)
        form_fields_bulk.append(field)
    FormFields.objects.bulk_create(form_fields_bulk)


def copy_template(form_id, target_id, new_title=None, creator=None):
    exist_template = FormTemplate.objects.filter(sys_id=target_id, from_template=form_id).first()
    if exist_template:
        return exist_template
    form_template = FormTemplate.objects.get(pk=form_id)
    form_template.sys_id = target_id
    form_template.title = new_title if new_title is not None else form_template.title
    form_template.pk = None
    form_template.id = None
    form_template.from_template_id = form_id
    form_template.creator = creator
    form_template.save()
    new_form_template = form_template
    form_template = FormTemplate.objects.get(pk=form_id)  # 重新获取源模板

    # 根据表单模版ID查找模版字段
    copy_field(form_template, new_form_template)
    return new_form_template


def make_m2m_proxy(template_field_from: FormFields):
    from org.models import Org
    from customer.models import Customer
    from goods.models import Goods
    from service.models import Services
    from usercenter.models import User, Department
    from parameter.models import Parameters
    from account.models import Account
    from article.models import Article
    from formtemplate.models import FormData
    from baseconfig.models import BaseTree

    models_map = {
        'org': Org,
        'customer': Customer,
        'goods': Goods,
        'service': Services,
        'user': User,
        'department': Department,
        'parameters': Parameters,
        'article': Article,
        'account': Account,
        'formdata': FormData,
        'basetree': BaseTree,
    }

    if not template_field_from.is_m2m or not template_field_from.related_template:
        raise ValueError('template_field_from is not a m2m field')
    from_model = template_field_from.template.get_model()
    to_model = template_field_from.related_template.get_model()

    class M2M_Proxy(ManyToManyData):
        from_m = ForeignKey(
            from_model, on_delete=DO_NOTHING, db_column='from_id', db_constraint=False, related_name='+'
        )
        to_m = ForeignKey(
            to_model, on_delete=DO_NOTHING, db_column='to_id', db_constraint=False, related_name='+'
        )

        class Meta:
            proxy = True
            app_label = 'formtemplate.' + template_field_from.pk

    return M2M_Proxy


class AliasModelBase(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        print('[AliasModelBase] __new__ attrs:', attrs)
        print('[AliasModelBase] __new__ kwargs:', kwargs)
        basic_fields = [
            'id', 'org_id', 'sys_id', 'biz_id', 'src_id', 'create_time', 'user', 'department', 'template'
        ]
        if 'template' in kwargs:
            template = kwargs['template']
            del kwargs['template']
            template_model = template.get_model()
            fields = template.fields.all()
            template_model_fields_map = {f.name: f for f in template_model._meta.fields}
            attrs.update({k: template_model_fields_map[k] for k in basic_fields if k in template_model_fields_map})
            sttrs_fields = {}
            for field in fields:
                if field.col_name in basic_fields:
                    continue
                if field.col_name == 'obj_id' and field.related_template:
                    sttrs_fields[field.alias] = ForeignKey(
                        to=field.related_template.get_model(), on_delete=DO_NOTHING,
                        null=True, blank=True, related_name='+', db_column='obj_id', db_constraint=False
                    )
                    continue
                if field.is_related:
                    continue
                try:
                    _name, path, _args, _kwargs = template_model_fields_map[field.col_name].deconstruct()
                    _kwargs['db_column'] = field.col_name
                    new_field = template_model_fields_map[field.col_name].__class__(*_args, **_kwargs)
                except KeyError:
                    print(f'Field "{field.col_name}" not found in "{template_model._meta.db_table}"')
                    continue
                sttrs_fields[field.alias] = new_field
                print(new_field.deconstruct())
            attrs.update(sttrs_fields)
            print('[AliasModelBase] __new__ attrs:', attrs)
        return super().__new__(cls, name, bases, attrs, **kwargs)


def build_template_proxy_model(template: 'FormTemplate', app_label='formtemplate') -> Type[Model]:
    template_model = template.get_model()
    meta = type('Meta', (), {'managed': False, 'app_label': app_label, 'db_table': template_model._meta.db_table})
    return AliasModelBase(
        'DataProxy_' + template.pk,
        (Model,),
        {'Meta': meta, '__module__': 'formtemplate.models'},
        template=template
    )  # type: ignore


def template_data_to_csv(template: 'FormTemplate', org_id=None, exclude_columns: Optional[List[str]] = None) -> str:
    if exclude_columns is None:
        exclude_columns = []
    model = template.get_model()
    fields = template.all_fields
    qs = model.objects.filter(template_id=template.pk)
    if org_id is not None:
        qs = qs.filter(org_id=org_id)
    serializer_class = template.get_serializer_class()
    data = serializer_class(qs, many=True).data
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)
    headers = [f.alias for f in fields if f.alias not in exclude_columns]
    desc_headers = [f.col_title for f in fields if f.alias not in exclude_columns]
    writer.writerow(desc_headers)
    for item in data:
        row = []
        for header in headers:
            if header in item:
                row.append(item[header])
            else:
                row.append('')
        writer.writerow(row)
    output = csv_file.getvalue()
    csv_file.close()
    return output


def build_qs_and_serializer_from_template_id(template_id: str):
    template = FormTemplate.objects.get(pk=template_id)
    model = template.get_model()
    qs = model.objects.filter(template_id=template.pk)
    serializer_class = template.get_serializer_class()
    return qs, serializer_class
