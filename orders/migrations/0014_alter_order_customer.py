# Generated by Django 4.2 on 2024-03-02 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0063_alter_customerprofile_first_name_and_more'),
        ('orders', '0013_alter_table_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_orders', to='users.customerprofile'),
        ),
    ]