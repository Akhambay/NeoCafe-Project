# Generated by Django 4.2 on 2024-02-12 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_rename_schedules_customuser_schedule'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='schedule',
        ),
    ]