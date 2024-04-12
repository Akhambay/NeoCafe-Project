# notification/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Notification

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if instance.order_status == "Готов":
        notification = Notification(order=instance)
        notification.save()


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if instance.order_status == "Готов":
        existing_notification = Notification.objects.filter(order=instance).first()
        if not existing_notification:
            notification = Notification(order=instance)
            notification.save()
