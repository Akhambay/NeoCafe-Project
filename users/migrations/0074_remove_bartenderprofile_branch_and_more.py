from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_bartenderprofile_user_type_waiterprofile_user_type'),
 ('users', '0072_bartenderprofile_branch_alter_profile_branch_and_more'),

    ]

    operations = [
	migrations.RemoveField(
            model_name='bartenderprofile',
            name='branch',
        ),
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='email',
        ),
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='schedule',
        ),
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='user_type',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='branch',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='email',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='schedule',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='waiterprofile',
            name='user_type',
        ),
        migrations.AddField(
            model_name='bartenderprofile',
            name='profile_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='waiterprofile',
            name='profile_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.profile'),
            preserve_default=False,
        ),
    ]
