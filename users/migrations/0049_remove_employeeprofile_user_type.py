# Generated by Django 4.2 on 2024-02-27 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0048_alter_employeeprofile_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeeprofile',
            name='user_type',
        ),
    ]