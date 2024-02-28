# Generated by Django 4.2 on 2024-02-28 17:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0062_rename_orders_customerprofile_order_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerprofile',
            old_name='order',
            new_name='orders',
        ),
        migrations.RemoveField(
            model_name='customerprofile',
            name='bonus_points',
        ),
        migrations.RemoveField(
            model_name='customerprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='bonus_points',
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='bonus',
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='customer',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customerprofile',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_type',
            field=models.CharField(choices=[('Waiter', 'Waiter'), ('Bartender', 'Bartender')], default='Waiter', max_length=50),
        ),
    ]