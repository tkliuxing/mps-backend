from django.contrib import admin
from . import models


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['pk', 'category', 'title', 'create_time', 'create_user', ]
