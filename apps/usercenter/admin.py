from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django_mptt_admin.admin import DjangoMpttAdmin
from . import models

# try:
#     admin.site.unregister(Group)
# except:
#     pass


@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = ['sys_id', 'org_id', 'username', 'full_name', 'department', 'is_active', 'is_superuser']
    list_display_links = ['sys_id', 'org_id', 'username', 'full_name', 'department']
    search_fields = ('username', 'full_name', 'email', 'mobile',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('department', 'full_name', 'mobile', 'email', )}),
        ('系统设置', {
            'fields': ('sys_id', 'org_id', ),
        }),
        ('功能权限', {
            'fields': ('func_groups', 'func_user_permissions', ),
        }),
        (_('Important dates'), {'fields': ('last_login', )}),
        ('用户状态', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_tester', ),
        }),
        ('微信信息', {'fields': ('wechart_name', 'wechart_avatar', 'wechart_oid', 'wechart_uid', )}),
    )
    filter_horizontal = ('func_groups', 'func_user_permissions', )
    list_filter = ('sys_id', 'org_id', 'is_staff', 'is_active', 'is_superuser', )
    search_fields = ('username', 'full_name', 'email', 'mobile',)


@admin.register(models.Department)
class DepartmentAdmin(DjangoMpttAdmin):
    class Media:
        css = {
            'all': (
                'js/nouislider.min.css',
                'css/admin-numeric-filter.css',
            )
        }
        js = (
            'js/wNumb.min.js',
            'js/nouislider.min.js',
            'js/admin-numeric-filter.js',
        )
    list_display = ['sys_id', 'org_id', 'name', 'parent', ]
    search_fields = ('name',)
    list_filter = ('sys_id', )
    tree_auto_open = 0


@admin.register(models.FuncGroup)
class FuncGroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)


@admin.register(models.FuncPermission)
class FuncPermissionAdmin(DjangoMpttAdmin):
    class Media:
        css = {
            'all': (
                'js/nouislider.min.css',
                'css/admin-numeric-filter.css',
            )
        }
        js = (
            'js/wNumb.min.js',
            'js/nouislider.min.js',
            'js/admin-numeric-filter.js',
        )
    search_fields = ('name', 'codename',)
    list_display = ['sys_id', 'name', 'codename', 'parent', ]
    list_filter = ('sys_id', )
    item_label_field_name = 'name'
    use_context_menu = True
    tree_auto_open = 0


@admin.register(models.PhoneAccess)
class PhoneAccessAdmin(admin.ModelAdmin):
    list_display = ['create_time', 'phone', 'phone_access',]
    ordering = ('-create_time',)
