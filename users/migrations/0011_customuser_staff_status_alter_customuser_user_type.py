# Generated by Django 4.2 on 2024-02-08 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_customuser_branch_alter_customuser_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='staff_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('waiter', 'Waiter'), ('bartender', 'Bartender'), ('customer', 'Customer')], default='admin', max_length=50),
        ),
    ]
