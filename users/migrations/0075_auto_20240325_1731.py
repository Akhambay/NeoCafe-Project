# Generated by Django 4.2 on 2024-03-25 12:31


from django.db import migrations

def delete_null_profile_ids(apps, schema_editor):
    BartenderProfile = apps.get_model('users', 'BartenderProfile')
    BartenderProfile.objects.filter(profile_ptr_id__isnull=True).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0074_remove_bartenderprofile_branch_and_more'),
    ]

    operations = [
        migrations.RunPython(delete_null_profile_ids),
    ]
