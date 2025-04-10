from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from .models import BaseTree, BaseConfigFileUpload


@admin.register(BaseTree)
class BaseTreeAdmin(DjangoMpttAdmin):
    list_display = ['sys_id', 'name', 'parent', ]
    list_display_links = list_display
    search_fields = ['sys_id', 'org_id', 'name',]


@admin.register(BaseConfigFileUpload)
class BaseConfigFileUploadAdmin(admin.ModelAdmin):
    list_display = ['sys_id', 'category', 'file']
    list_display_links = list_display
    search_fields = ['sys_id', 'org_id', 'category__name', ]
