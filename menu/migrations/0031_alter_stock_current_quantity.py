# Generated by Django 4.2 on 2024-03-21 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0030_alter_stock_current_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='current_quantity',
            field=models.IntegerField(),
        ),
    ]
