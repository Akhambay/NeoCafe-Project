# Generated by Django 4.2 on 2024-02-17 18:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_alter_customuser_user_type'),
        ('menu', '0013_remove_menu_item_ingredients_ingredient_menu_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu_item',
            name='branch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='users.branch'),
            preserve_default=False,
        ),
    ]
