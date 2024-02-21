# Generated by Django 4.2 on 2024-02-18 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0020_remove_stock_menu_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='stock',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='menu.stock'),
            preserve_default=False,
        ),
    ]