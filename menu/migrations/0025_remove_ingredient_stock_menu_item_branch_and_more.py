# Generated by Django 4.2 on 2024-02-18 18:38

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_alter_customuser_user_type'),
        ('menu', '0024_ingredient_stock_alter_category_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='stock',
        ),
        migrations.AddField(
            model_name='menu_item',
            name='branch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='users.branch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stock',
            name='is_enough',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(default='Выпечка', max_length=100, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
        migrations.AlterField(
            model_name='menu_item',
            name='category',
            field=models.ForeignKey(default='Выпечка', on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='menu.category'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='type',
            field=models.CharField(choices=[('Готовое', 'Готовое изделие'), ('Cырье', 'Cырье')], max_length=15),
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
    ]
