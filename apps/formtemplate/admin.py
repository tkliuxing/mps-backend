from django.contrib import admin
from . import models


@admin.register(models.FormFields)
class FormFieldsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'org_id', 'biz_id', 'template', 'col_title', 'alias', 'col_name', ]
    list_filter = ['sys_id', ]
    search_fields = ['col_title', 'alias', 'col_name', ]


@admin.register(models.FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'org_id', 'biz_id', 'title', 'form_type', 'sort_num', 'create_time', ]
    list_filter = ['sys_id', 'biz_id', ]
    search_fields = ['title', ]


@admin.register(models.FormDataReportConf)
class FormDataReportConfAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'org_id', 'biz_id', 'report_id', 'report_name', 'creator']
    search_fields = ['report_id', 'report_name']
