# Generated by Django 4.2 on 2024-03-03 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0063_alter_customerprofile_first_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerprofile',
            old_name='bonus',
            new_name='bonus_points',
        ),
    ]