# Generated by Django 4.2 on 2024-02-23 04:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_alter_bartenderprofile_last_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bartenderprofile',
            old_name='schedule',
            new_name='employee_schedules',
        ),
        migrations.RenameField(
            model_name='waiterprofile',
            old_name='schedule',
            new_name='employee_schedules',
        ),
    ]
