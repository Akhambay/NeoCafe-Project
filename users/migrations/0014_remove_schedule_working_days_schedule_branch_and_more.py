# Generated by Django 4.2 on 2024-02-11 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_branch_schedule_remove_customuser_schedule_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='working_days',
        ),
        migrations.AddField(
            model_name='schedule',
            name='branch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='users.branch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_friday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_monday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_saturday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_sunday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_thursday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_tuesday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='day_wednesday',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='end_time',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='start_time',
            field=models.TimeField(),
        ),
    ]
