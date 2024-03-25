# delete_null_profile_ids.py

from django.core.management.base import BaseCommand
from users.models import BartenderProfile


class Command(BaseCommand):
    help = 'Deletes rows from users_bartenderprofile where profile_ptr_id is NULL'

    def handle(self, *args, **options):
        null_profiles = BartenderProfile.objects.filter(
            profile_ptr_id__isnull=True)
        null_profiles.delete()
        self.stdout.write(self.style.SUCCESS(
            'Deleted rows with NULL profile_ptr_id'))
