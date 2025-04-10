from django.contrib import admin
from . import models


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'org_id', 'user', 'obj_id']


@admin.register(models.AccountStatements)
class AccountStatementsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'sys_id', 'org_id', 'acc', 'acc_name', 'record_type', 'amount', 'used_amount', 'end_time']
    ordering = ['-create_time']
