# Generated by Django 4.2 on 2024-02-22 08:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_remove_ordereditem_price_order_total_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employeeprofile',
            name='employee',
        ),
        migrations.DeleteModel(
            name='CustomerProfile',
        ),
        migrations.DeleteModel(
            name='EmployeeProfile',
        ),
    ]