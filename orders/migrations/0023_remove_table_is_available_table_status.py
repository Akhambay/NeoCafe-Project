# Generated by Django 4.2 on 2024-03-13 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_remove_table_status_table_is_available'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='table',
            name='is_available',
        ),
        migrations.AddField(
            model_name='table',
            name='status',
            field=models.CharField(choices=[('Reserved', 'Reserved'), ('Available', 'Available')], default='Reserved', max_length=20),
        ),
    ]
