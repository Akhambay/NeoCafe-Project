# Generated by Django 4.2 on 2024-03-21 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0029_alter_category_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='current_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]