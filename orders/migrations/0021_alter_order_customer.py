# Generated by Django 4.2 on 2024-03-03 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0066_remove_customerprofile_orders'),
        ('orders', '0020_alter_order_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='users.customerprofile'),
        ),
    ]
