# Generated by Django 3.2.11 on 2022-02-15 14:59

from django.db import migrations
import utility.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_auto_20220215_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smsconfig',
            name='id',
            field=utility.db_fields.TableNamePKField('SYSSMS', serialize=False),
        ),
        migrations.AlterField(
            model_name='system',
            name='id',
            field=utility.db_fields.TableNamePKField('SYS', serialize=False),
        ),
        migrations.AlterField(
            model_name='systemlog',
            name='id',
            field=utility.db_fields.TableNamePKField('SYSLOG', serialize=False),
        ),
        migrations.AlterField(
            model_name='systemorg',
            name='id',
            field=utility.db_fields.TableNamePKField('SYSORG', serialize=False),
        ),
        migrations.AlterField(
            model_name='systemproject',
            name='id',
            field=utility.db_fields.TableNamePKField('SYSP', serialize=False),
        ),
        migrations.AlterField(
            model_name='wechatconfig',
            name='id',
            field=utility.db_fields.TableNamePKField('SYSWC', serialize=False),
        ),
    ]
