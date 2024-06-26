# Generated by Django 4.2 on 2024-03-29 04:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0037_alter_order_branch_customerorder'),
        ('users', '0078_alter_customerprofile_orders_alter_customuser_orders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerprofile',
            name='orders',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_profile', to='orders.customerorder'),
        ),
    ]
