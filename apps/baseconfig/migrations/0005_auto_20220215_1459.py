# Generated by Django 3.2.11 on 2022-02-15 14:59

from django.db import migrations
import utility.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('baseconfig', '0004_auto_20220119_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseconfigfileupload',
            name='id',
            field=utility.db_fields.TableNamePKField('files', serialize=False),
        ),
        migrations.AlterField(
            model_name='basetree',
            name='id',
            field=utility.db_fields.TableNamePKField('bt', serialize=False),
        ),
    ]
