# Generated by Django 3.2.10 on 2022-01-13 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0004_auto_20220106_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='org',
            name='name',
            field=models.CharField(blank=True, help_text='名称', max_length=256, null=True, verbose_name='名称'),
        ),
    ]
