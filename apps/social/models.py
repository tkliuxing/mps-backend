from utility.db_fields import TableNamePKField
from django.db import models


# 发现用户动态信息
class SocialDynamic(models.Model):
    """用户动态信息"""
    VISIBLE_TYPE = (
        ('所有人可见', '所有人可见'),
        ('仅自己可见', '仅自己可见'),
        ('好友可见', '好友可见'),
    )
    id = TableNamePKField('sd')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    user = models.ForeignKey('usercenter.User', verbose_name='发布者', on_delete=models.CASCADE,
                             help_text='user_id to usercenter_user', db_constraint=False)
    publish_time = models.DateTimeField('发布时间', auto_now_add=True)
    title = models.CharField('标题', max_length=128, null=True, blank=True)
    content = models.TextField('发布内容', null=True, blank=True, help_text='发布内容')
    visible = models.CharField('可见性', choices=VISIBLE_TYPE, max_length=15,
                               help_text='可见性: 所有人可见, 仅自己可见, 好友可见')
    is_anonymous = models.BooleanField('是否匿名发布', default=False, help_text='是否匿名发布: default false')
    address = models.CharField('所在位置', max_length=500, null=True, blank=True, help_text='所在位置')
    images = models.TextField('用户动态图片', null=True, blank=True, help_text='用户动态图片JSON数组')
    is_hot = models.BooleanField('热门', default=False, help_text='热门')
    is_pub = models.BooleanField('精选', default=False, help_text='精选')
    is_deleted = models.BooleanField('被删除', default=False, help_text='被删除')
    desc = models.TextField('附加字段', null=True, blank=True, help_text='附加字段')

    class Meta:
        verbose_name = 'Social: 动态'
        verbose_name_plural = verbose_name
        ordering = ['-publish_time']

    def __str__(self):
        return '{0}: 内容: {1}'.format(self.user, self.content[:10])


# 发现用户评论信息
class SocialComment(models.Model):
    """发现用户评论信息"""
    id = TableNamePKField('sc')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    user = models.ForeignKey('usercenter.User', verbose_name='评论者', related_name='commenter',
                             on_delete=models.CASCADE, help_text='user_id to usercenter_user', db_constraint=False)
    be_commented = models.ForeignKey('usercenter.User', verbose_name='被评论者', related_name='be_commented',
                                     on_delete=models.CASCADE, help_text='be_commented_id to usercenter_user',
                                     db_constraint=False)
    content = models.CharField('评论内容', max_length=255)
    comment_time = models.DateTimeField('评论时间', auto_now_add=True)
    thumbs_up = models.PositiveIntegerField('点赞数量', default=0)
    associated = models.ForeignKey('SocialDynamic', verbose_name='所评用户动态', on_delete=models.CASCADE,
                                   related_name='comments', help_text='associated_id to social_socialdynamic')

    class Meta:
        verbose_name = 'Social: 评论'
        verbose_name_plural = verbose_name
        ordering = ['-comment_time']

    def __str__(self):
        return "{0}".format(self.content)


# 发现用户点赞信息
class SocialPraise(models.Model):
    """发现用户点赞信息"""
    id = TableNamePKField('sp')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    user = models.ForeignKey('usercenter.User', verbose_name='点赞者', related_name='thumbs_up',
                             on_delete=models.CASCADE, help_text='user_id to usercenter_user', db_constraint=False)
    be_thumbs_up = models.ForeignKey('usercenter.User', verbose_name='被点赞者', related_name='be_thumbs_up',
                                     on_delete=models.CASCADE, help_text='be_thumbs_up_id to usercenter_user',
                                     db_constraint=False)
    thumbs_up_time = models.DateTimeField('点赞时间', auto_now_add=True)
    thumbs_up_dynamic = models.ForeignKey('SocialDynamic', verbose_name='所赞动态', on_delete=models.CASCADE,
                                          related_name='thumbs_up',
                                          help_text='thumbs_up_dynamic_id to social_socialdynamic', db_constraint=False)

    class Meta:
        verbose_name = 'Social: 点赞'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'thumbs_up_dynamic',)
