# Generated by Django 4.2.11 on 2024-04-17 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0008_rename_is_read_notification_read_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='position',
        ),
    ]
