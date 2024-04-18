# Generated by Django 4.2.11 on 2024-04-17 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0034_extraitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extraitem',
            name='choice_category',
        ),
        migrations.AddField(
            model_name='extraitem',
            name='measurement_unit',
            field=models.CharField(default='мл', max_length=15),
        ),
    ]