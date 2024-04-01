# Generated by Django 4.2 on 2024-02-18 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0018_alter_category_name_alter_menu_item_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='menu_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='menu.menu_item'),
            preserve_default=False,
        ),
    ]
