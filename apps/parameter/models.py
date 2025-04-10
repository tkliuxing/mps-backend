from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from utility.id_gen import gen_new_id


# 常用参数表
class Parameters(MPTTModel):
    category = models.CharField('参数分类', max_length=16, help_text='参数分类名称')
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=64, null=True, blank=True)
    field_01 = models.CharField(max_length=64, null=True, blank=True)
    field_02 = models.CharField(max_length=64, null=True, blank=True)
    field_03 = models.CharField(max_length=64, null=True, blank=True)
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', verbose_name='上级',
        db_index=True, on_delete=models.CASCADE, help_text='上级')
    remark = models.TextField('备注', null=True, blank=True, help_text='备注')
    field_json = models.TextField('JSON字段', null=True, blank=True, help_text='JSON字段')

    class Meta:
        verbose_name = '常用参数表'
        verbose_name_plural = verbose_name

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_path_name(self):
        names = self.get_ancestors(include_self=True).values_list('name', flat=True)
        return "/".join(names)

    @classmethod
    def category_to_basetree(cls, category, sys_id, org_id, biz_id):
        from baseconfig.models import BaseTree
        root_nodes = cls.objects.filter(category=category, parent__isnull=True)
        # is_leaf = nodes[0].is_leaf_node()
        root_node = BaseTree.objects.create(
            id=gen_new_id('bt'),
            sys_id=sys_id,
            org_id=org_id,
            biz_id=biz_id,
            name=category,
        )
        level_parent = {0: root_node}
        for root in root_nodes:
            nodes = root.get_descendants(include_self=True).order_by('lft')
            for node in nodes:
                BaseTree.objects.create(
                    id=gen_new_id('bt'),
                    sys_id=sys_id,
                    org_id=org_id,
                    biz_id=biz_id,
                    name=node.name,
                    arguments=node.value,
                    field_01=node.field_01,
                    field_02=node.field_02,
                    field_03=node.field_03,
                    description=node.remark,
                    text_01=node.field_json,
                    parent=level_parent.get(node.level)
                )
                if not node.is_leaf_node():
                    level_parent[node.level+1] = node

    def to_basetree(self, sys_id, org_id, biz_id):
        from baseconfig.models import BaseTree
        nodes = self.get_descendants(include_self=False).order_by('lft')
        root_node = BaseTree.objects.create(
            id=gen_new_id('bt'),
            sys_id=sys_id,
            org_id=org_id,
            biz_id=biz_id,
            name=self.name,
            arguments=self.value,
            field_01=self.field_01,
            field_02=self.field_02,
            field_03=self.field_03,
            description=self.remark,
            text_01=self.field_json,
        )
        level_parent = {self.level+1: root_node}
        for node in nodes:
            bt_node = BaseTree.objects.create(
                id=gen_new_id('bt'),
                sys_id=sys_id,
                org_id=org_id,
                biz_id=biz_id,
                name=node.name,
                arguments=node.value,
                field_01=node.field_01,
                field_02=node.field_02,
                field_03=node.field_03,
                description=node.remark,
                text_01=node.field_json,
                parent=level_parent.get(node.level)
            )
            if not node.is_leaf_node():
                level_parent[node.level+1] = bt_node
