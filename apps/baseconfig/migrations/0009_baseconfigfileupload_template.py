# Generated by Django 3.2.11 on 2023-10-17 09:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formtemplate', '0011_auto_20230829_1504'),
        ('baseconfig', '0008_alter_baseconfigfileupload_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseconfigfileupload',
            name='template',
            field=models.ForeignKey(blank=True, help_text='模板', null=True, on_delete=django.db.models.deletion.CASCADE, to='formtemplate.formtemplate'),
        ),
    ]
