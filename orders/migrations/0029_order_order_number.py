# Generated by Django 4.2 on 2024-03-20 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0028_alter_order_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.PositiveIntegerField(default=3001, unique=False),
            preserve_default=False,
        ),
    ]