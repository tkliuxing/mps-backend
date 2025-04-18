# Generated by Django 3.2.11 on 2022-04-28 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_auto_20220215_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemlog',
            name='log_type',
            field=models.CharField(blank=True, db_index=True, help_text='日志类别', max_length=16, null=True, verbose_name='日志类别'),
        ),
        migrations.AlterField(
            model_name='systemlog',
            name='org_id',
            field=models.IntegerField(db_index=True, default=1, verbose_name='组织ID'),
        ),
    ]
