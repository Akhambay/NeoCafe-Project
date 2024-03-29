# Generated by Django 4.2 on 2024-02-17 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0011_remove_menu_item_branch_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=225)),
                ('quantity', models.PositiveIntegerField()),
                ('measurement_unit', models.CharField(choices=[('гр', 'гр'), ('кг', 'кг'), ('мл', 'мл'), ('л', 'л'), ('шт', 'шт')], max_length=15)),
            ],
        ),
        migrations.RemoveField(
            model_name='menu_item',
            name='branch_stock',
        ),
        migrations.CreateModel(
            name='MenuItemIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.ingredient')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.menu_item')),
            ],
        ),
        migrations.AddField(
            model_name='menu_item',
            name='ingredients',
            field=models.ManyToManyField(blank=True, related_name='menu_items', through='menu.MenuItemIngredient', to='menu.ingredient'),
        ),
    ]
