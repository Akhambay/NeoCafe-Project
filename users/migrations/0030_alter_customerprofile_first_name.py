# Generated by Django 4.2 on 2024-02-22 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_rename_name_customerprofile_first_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerprofile',
            name='first_name',
            field=models.CharField(default=' ', max_length=50),
        ),
    ]
