# Generated by Django 4.2 on 2024-02-16 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_remove_customuser_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('Waiter', 'Waiter'), ('Bartender', 'Bartender')], default='Waiter', max_length=50),
        ),
    ]
