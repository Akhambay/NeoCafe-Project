# Generated by Django 4.2.11 on 2024-04-16 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0042_remove_itemtoorder_extra_product_and_more'),
        ('menu', '0032_extraitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ExtraItem',
        ),
    ]
