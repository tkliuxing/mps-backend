# Generated by Django 3.2.10 on 2021-12-29 15:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utility.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('baseconfig', '0001_initial'),
        ('usercenter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', utility.db_fields.TableNamePKField(blank=True, default=None, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('sys_id', models.IntegerField(db_index=True, default=1, verbose_name='系统ID')),
                ('org_id', models.IntegerField(db_index=True, default=1, verbose_name='组织ID')),
                ('biz_id', models.IntegerField(db_index=True, default=1, verbose_name='业务ID')),
                ('src_id', models.IntegerField(db_index=True, default=1, verbose_name='数据源ID')),
                ('title', models.CharField(help_text='标题', max_length=255, verbose_name='标题')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('content', models.TextField(blank=True, help_text='内容', null=True, verbose_name='内容')),
                ('cover_image', models.TextField(blank=True, help_text='封面图片', null=True, verbose_name='封面图片')),
                ('category', models.ForeignKey(blank=True, db_constraint=False, help_text='栏目ID category_id to baseconfig_basetree', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='baseconfig.basetree')),
                ('create_user', models.ForeignKey(blank=True, db_constraint=False, help_text='创建人ID create_user_id to usercenter_user', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('department', models.ForeignKey(blank=True, db_constraint=False, help_text='department_id to usercenter_department', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='usercenter.department')),
            ],
            options={
                'verbose_name': '02. 文章',
                'verbose_name_plural': '02. 文章',
                'ordering': ['-create_time', 'category'],
            },
        ),
    ]
