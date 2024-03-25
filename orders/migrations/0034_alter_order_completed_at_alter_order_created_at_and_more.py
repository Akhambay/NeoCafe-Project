# Generated by Django 4.2 on 2024-03-25 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0033_alter_order_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='completed_at',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.TimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='updated_at',
            field=models.TimeField(auto_now=True),
        ),
    ]
