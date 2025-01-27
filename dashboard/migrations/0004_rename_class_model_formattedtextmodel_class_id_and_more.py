# Generated by Django 5.1.3 on 2025-01-14 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_rename_class_model_scenariomodel_class_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formattedtextmodel',
            old_name='class_model',
            new_name='class_id',
        ),
        migrations.RenameField(
            model_name='studentnotemodel',
            old_name='class_model',
            new_name='class_id',
        ),
        migrations.AlterField(
            model_name='scenariomodel',
            name='conversation_starter',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scenariomodel',
            name='role_polly',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='scenariomodel',
            name='role_student',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
