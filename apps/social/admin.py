from django.contrib import admin
from . import models


@admin.register(models.SocialDynamic)
class SocialDynamicAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'org_id', 'biz_id', 'user', 'publish_time', 'title', 'content', 'visible', 'is_anonymous', 'address', 'images', 'is_hot', 'is_pub', 'is_deleted', 'desc', ]


@admin.register(models.SocialComment)
class SocialCommentAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'be_commented', 'content', 'comment_time', 'thumbs_up', 'associated', ]


@admin.register(models.SocialPraise)
class SocialPraiseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'be_thumbs_up', 'thumbs_up_time', 'thumbs_up_dynamic', ]
