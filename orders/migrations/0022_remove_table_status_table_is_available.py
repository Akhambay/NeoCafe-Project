# Generated by Django 4.2 on 2024-03-13 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_alter_order_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='table',
            name='status',
        ),
        migrations.AddField(
            model_name='table',
            name='is_available',
            field=models.BooleanField(default=False),
        ),
    ]
