from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_bartenderprofile_user_type_waiterprofile_user_type'),
    ]

    operations = [
        # Drop the temporary profile_ptr_id_temp column
        migrations.RemoveField(
            model_name='bartenderprofile',
            name='profile_ptr_id_temp',
        ),
    ]
