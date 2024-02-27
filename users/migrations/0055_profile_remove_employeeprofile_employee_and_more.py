# Generated by Django 4.2 on 2024-02-27 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0054_rename_employee_profile_bartenderprofile_employee_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('user_type', models.CharField(choices=[('Waiter', 'Waiter'), ('Bartender', 'Bartender')], default='Waiter', max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='employeeprofile',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='employeeprofile',
            name='schedule',
        ),
    ]
