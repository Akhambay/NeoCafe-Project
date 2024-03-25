from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_bartenderprofile_user_type_waiterprofile_user_type'),
    ]

    operations = [
        # Add a new field to store the temporary profile_ptr_id
        migrations.AddField(
            model_name='bartenderprofile',
            name='profile_ptr_id_temp',
            field=models.IntegerField(null=True),
            preserve_default=False,
        ),
        # Set temporary profile_ptr_id values based on the existing profile_ptr values
        migrations.RunSQL(
            "UPDATE users_bartenderprofile SET profile_ptr_id_temp = profile_ptr_id",
            "UPDATE users_bartenderprofile SET profile_ptr_id = profile_ptr_id_temp",
        ),
        # Remove the NOT NULL constraint from profile_ptr_id_temp column
        migrations.AlterField(
            model_name='bartenderprofile',
            name='profile_ptr_id_temp',
            field=models.IntegerField(null=True),
        ),
        # Drop the temporary profile_ptr_id_temp column
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='profile_ptr_id_temp',
        ),
    ]
