# Generated by Django 3.2.11 on 2022-01-20 11:04

from django.db import migrations
import utility.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0006_auto_20220119_1110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goods',
            name='obj_type',
        ),
        migrations.AlterField(
            model_name='goods',
            name='id',
            field=utility.db_fields.TableNamePKField(blank=True, default=utility.db_fields.TableNamePKField.auto_id, editable=False, max_length=32, prefix='G', primary_key=True, serialize=False),
        ),
    ]
