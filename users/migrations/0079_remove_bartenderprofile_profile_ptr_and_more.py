# Generated by Django 4.2 on 2024-03-25 20:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0078_bartenderprofile_email_bartenderprofile_first_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='profile_ptr',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='profile_ptr',
        ),
        migrations.AddField(
            model_name='bartenderprofile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='bartenderprofile',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bartenderprofile',
            name='id',
            field=models.BigAutoField(auto_created=True, default=30, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bartenderprofile',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='waiterprofile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='waiterprofile',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='waiterprofile',
            name='id',
            field=models.BigAutoField(auto_created=True, default=40, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='waiterprofile',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='bartenderprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bartenderprofile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='bartenderprofile',
            name='user_type',
            field=models.CharField(choices=[('Bartender', 'Bartender')], default='Bartender', max_length=50),
        ),
        migrations.AlterField(
            model_name='waiterprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiterprofile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='waiterprofile',
            name='user_type',
            field=models.CharField(choices=[('Waiter', 'Waiter')], default='Waiter', max_length=50),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('user_type', models.CharField(choices=[('Waiter', 'Waiter'), ('Bartender', 'Bartender')], default='Waiter', max_length=50)),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='users.branch')),
                ('schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.employeeschedule')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
