# Generated by Django 4.2 on 2024-03-22 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0071_profile_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='bartenderprofile',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bartender', to='users.branch'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee', to='users.branch'),
        ),
        migrations.AlterField(
            model_name='waiterprofile',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiters', to='users.branch'),
        ),
    ]
