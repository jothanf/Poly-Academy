# Generated by Django 5.1.3 on 2025-01-16 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_teachermodel_profile_picture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmodel',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='student_profile_pictures/'),
        ),
    ]