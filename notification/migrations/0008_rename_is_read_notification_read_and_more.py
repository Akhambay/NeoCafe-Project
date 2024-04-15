# Generated by Django 4.2.11 on 2024-04-15 12:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notification', '0007_rename_timestamp_notification_created_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='is_read',
            new_name='read',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='created_at',
            new_name='timestamp',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='order',
        ),
        migrations.AddField(
            model_name='notification',
            name='description',
            field=models.TextField(default='eee'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='position',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='notification',
            name='recipient',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='status',
            field=models.CharField(default='Новый', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]