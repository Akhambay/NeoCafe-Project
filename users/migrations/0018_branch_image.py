# Generated by Django 4.2 on 2024-02-11 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_remove_schedule_working_days_schedule_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='branch_images/'),
        ),
    ]