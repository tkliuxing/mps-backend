# Generated by Django 4.2.8 on 2024-08-27 16:04

from django.db import migrations, models
import utility.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('usercenter', '0022_alter_user_data_permission'),
        ('formtemplate', '0014_alter_formtemplate_department_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManyToManyData',
            fields=[
                ('id', utility.db_fields.TableNamePKField('MTM', editable=False, serialize=False)),
                ('m_from', models.CharField(db_column='from_id', db_index=True, max_length=32, verbose_name='M1 ID')),
                ('m_to', models.CharField(db_column='to_id', db_index=True, max_length=32, verbose_name='M2 ID')),
            ],
            options={
                'verbose_name': '03.多对多数据',
                'verbose_name_plural': '03.多对多数据',
                'db_table': 'formtemplate_mtm',
            },
        ),
        migrations.AddField(
            model_name='formfields',
            name='is_m2m',
            field=models.BooleanField(default=False, help_text='多对多关联', verbose_name='多对多关联'),
        ),
        migrations.AlterField(
            model_name='formtemplate',
            name='department',
            field=models.ManyToManyField(blank=True, help_text='部门ID数组', related_name='+', to='usercenter.department', verbose_name='usercenter_department.id'),
        ),
    ]
