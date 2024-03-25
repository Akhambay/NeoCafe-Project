from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0074_remove_bartenderprofile_branch_and_more'),
    ]

    operations = [
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
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bartenderprofile',
            name='profile_ptr',
            field=models.AutoField(default=0, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='bartenderprofile',
            name='user_type',
            field=models.CharField(choices=[('Waiter', 'Waiter'), ('Bartender', 'Bartender')], default='Waiter', max_length=50),
        ),
        migrations.AlterField(
            model_name='bartenderprofile',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bartender_profiles', to='users.Branch'),
        ),
        migrations.AlterField(
            model_name='bartenderprofile',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.EmployeeSchedule'),
        ),
        migrations.AlterField(
            model_name='bartenderprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bartender_profile', to=settings.AUTH_USER_MODEL),
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
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='waiterprofile',
            name='profile_ptr',
            field=models.AutoField(default=0, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='waiterprofile',
            name='user_type',
            field=models.CharField(choices=[('Waiter', 'Waiter'), ('Bartender', 'Bartender')], default='Waiter', max_length=50),
        ),
        migrations.AlterField(
            model_name='waiterprofile',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiter_profiles', to='users.Branch'),
        ),
        migrations.AlterField(
            model_name='waiterprofile',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.EmployeeSchedule'),
        ),
        migrations.AlterField(
            model_name='waiterprofile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiter_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
