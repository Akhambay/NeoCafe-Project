# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notifications.signals import notify


@receiver(post_save, sender=get_user_model())
def send_employee_added_notification(sender, instance, created, **kwargs):
    if created:
        notify.send(
            instance, recipient=instance,
            verb='added', description='You have been added as an employee.'
        )
