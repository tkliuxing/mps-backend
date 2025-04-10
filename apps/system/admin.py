from django.contrib import admin
from . import models


@admin.register(models.System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'name', ]


@admin.register(models.WechatConfig)
class WechatConfigAdmin(admin.ModelAdmin):
    list_display = ['pk', 'system', 'mp_name', ]
    list_filter = ['system', ]
    search_fields = ['mp_name', ]


@admin.register(models.SMSConfig)
class SMSConfigAdmin(admin.ModelAdmin):
    list_display = ['pk', 'system', 'name', 'sms_type', 'is_enabled', ]
    list_display_links = ['pk', 'system', 'name', 'sms_type', 'is_enabled', ]
