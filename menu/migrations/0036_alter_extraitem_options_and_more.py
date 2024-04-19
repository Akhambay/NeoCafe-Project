# Generated by Django 4.2.11 on 2024-04-19 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0035_remove_extraitem_choice_category_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='extraitem',
            options={'ordering': ['name'], 'verbose_name_plural': 'Доп. Продукты'},
        ),
        migrations.RemoveField(
            model_name='extraitem',
            name='measurement_unit',
        ),
        migrations.AddField(
            model_name='extraitem',
            name='choice_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='extra_products', to='menu.category'),
        ),
        migrations.AlterField(
            model_name='extraitem',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название доп. продукта'),
        ),
        migrations.AlterField(
            model_name='extraitem',
            name='type_extra_product',
            field=models.CharField(choices=[('Молоко', 'Молоко'), ('Сироп', 'Сиропы')], max_length=20, null=True, verbose_name='Доп. Продукт'),
        ),
    ]
