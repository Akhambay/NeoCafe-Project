# Generated by Django 4.2 on 2024-02-27 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0053_rename_employee_bartenderprofile_employee_profile_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bartenderprofile',
            old_name='employee_profile',
            new_name='employee',
        ),
        migrations.RenameField(
            model_name='waiterprofile',
            old_name='employee_profile',
            new_name='employee',
        ),
    ]
