# Generated by Django 3.2.10 on 2021-12-31 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usercenter', '0002_user_create_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.CharField(default='已通过', max_length=8, verbose_name='审核状态'),
        ),
    ]
