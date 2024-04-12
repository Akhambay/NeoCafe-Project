from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from orders.models import Order, ItemToOrder

@receiver(post_save, sender=Order, dispatch_uid="order_waiter_status_changed")
def waiter_status_changed(sender, instance, created, **kwargs):
    item_descriptions = []
    for ito in instance.ITO.all():  # Using custom related name 'ITO'
        item_descriptions.append(f"{ito.item.name} x {ito.quantity}")
    items_detail = ", ".join(item_descriptions)

    title = ""
    description = ""

    if instance.order_status == 'Новый':
        title = f"Ваш заказ оформлен"
        description = f"{items_detail}"
    elif instance.order_status == 'Готов':
        title = f"Заказ готов"
        description = f"{items_detail}"
    elif instance.order_status == 'В процессе':
        title = f"Бариста принял заказ"
        description = f"{items_detail}"
    elif instance.order_status == 'Завершен':
        title = f"Закрытие счета"
        description = f"{items_detail}"

    if title and description and instance.employee:
        Notification.objects.create(
            title=title,
            description=description,
            recipient=instance.employee,
            status=instance.order_status
        )

        employee_name = f"waiter-{instance.employee.id}"

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            employee_name,
            {
                "type": "get_notifications_handler",
            }
        )
