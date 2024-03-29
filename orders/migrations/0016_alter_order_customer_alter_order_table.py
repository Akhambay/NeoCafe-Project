# Generated by Django 4.2 on 2024-03-03 19:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0015_alter_order_customer_alter_order_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='table',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.table'),
        ),
    ]
