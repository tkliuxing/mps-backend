from django.contrib import admin
from . import models


@admin.register(models.MailBox)
class MailBoxAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'from_user', 'title', 'create_time', 'is_read')
    list_display_links = ('pk', 'user', 'from_user', 'title', 'create_time')


@admin.register(models.NoticePool)
class NoticePoolAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'channel', 'title', 'content', 'send_time', 'is_circulation', 'is_sent', 'from_user_display', 'create_time', ]
    list_display_links = ['pk', 'sys_id', 'channel', 'title', 'content', 'send_time', 'from_user_display', 'create_time', ]
    list_filter = ['channel', 'is_sent', 'is_circulation']
