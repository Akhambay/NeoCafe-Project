# Generated by Django 4.2 on 2024-02-19 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0025_remove_ingredient_stock_menu_item_branch_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu_item',
            name='branch',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]