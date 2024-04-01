# Generated by Django 4.2 on 2024-02-17 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0012_ingredient_remove_menu_item_branch_stock_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu_item',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='menu_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='menu.menu_item'),
            preserve_default=False,
        ),
    ]
