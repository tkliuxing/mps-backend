from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from . import models


@admin.register(models.Parameters)
class ParametersAdmin(DjangoMpttAdmin):
    list_display = ['pk', 'category', 'name', 'value']
    list_filter = ('category',)
