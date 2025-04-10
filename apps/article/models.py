from django.db import models
from utility.db_fields import TableNamePKField


class Article(models.Model):
    """文章"""
    id = TableNamePKField('art')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    category = models.ForeignKey(
        'baseconfig.BaseTree', on_delete=models.SET_NULL, null=True, blank=True, db_constraint=False,
        related_name='articles', help_text='栏目ID category_id to baseconfig_basetree')
    title = models.CharField('标题', max_length=255, help_text='标题')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    create_user = models.ForeignKey('usercenter.User', on_delete=models.SET_NULL, db_constraint=False,
                                    null=True, blank=True, verbose_name='创建人',
                                    help_text='创建人ID create_user_id to usercenter_user')
    content = models.TextField('内容', null=True, blank=True, help_text='内容')
    cover_image = models.TextField('封面图片', null=True, blank=True, help_text='封面图片')

    class Meta:
        verbose_name = '02. 文章'
        verbose_name_plural = verbose_name
        ordering = ['-create_time', 'category']

    def __str__(self):
        return self.title

    @property
    def category_name(self):
        return self.category.name if self.category else ''
