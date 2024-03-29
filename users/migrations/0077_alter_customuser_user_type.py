# Generated by Django 4.2 on 2024-03-28 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0076_customerprofile_orders_alter_customerprofile_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('Waiter', 'Waiter'), ('Bartender', 'Bartender'), ('Customer', 'Customer')], default='Waiter', max_length=50),
        ),
    ]