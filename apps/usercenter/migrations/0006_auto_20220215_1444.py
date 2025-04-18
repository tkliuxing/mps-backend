# Generated by Django 3.2.11 on 2022-02-15 14:44

from django.db import migrations, models
import utility.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('usercenter', '0005_auto_20220119_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funcgroup',
            name='permissions',
            field=models.ManyToManyField(blank=True, db_constraint=False, help_text='通过中间表 usercenter_funcgroup_permissions 关联 usercenter_funcpermission', to='usercenter.FuncPermission', verbose_name='功能权限'),
        )
    ]
