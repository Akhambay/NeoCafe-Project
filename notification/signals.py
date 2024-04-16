import time

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from loguru import logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from menu.models import Menu_Item
from menu.models import Branch
from menu.models import Stock
from orders.models import Order
from users.models import CustomUser
from .models import Notification

SLEEP_TIME = 3

User = get_user_model()


@receiver(post_save, sender=Notification)
def notify_customers(sender, instance, **kwargs):
    """
    Updates notifications on customer side.
    """
    logger.info("Updating notifications")
    time.sleep(SLEEP_TIME)
    channel_layer = get_channel_layer()  # Use this function
    async_to_sync(channel_layer.group_send)(
        "branch",
        {
            "type": "get_notifications",
        },
    )
    logger.info("Updating notifications")


@receiver(post_delete, sender=Notification)
def notify_customers_on_delete(sender, instance, **kwargs):
    logger.info("Updating notifications")
    time.sleep(SLEEP_TIME)
    channel_layer = get_channel_layer()  # Use this function
    async_to_sync(channel_layer.group_send)(
        "branch",
        {
            "type": "get_notifications",
        },
    )

@receiver(post_save, sender=Order, dispatch_uid="order_customer_status_changed")
def customer_status_changed(sender, instance, created, **kwargs):
    logger.info(f"Signal received for order with id {instance.id}. Created: {created}")

    item_descriptions = [f"{item.menu_item.name} x {item.quantity}" for item in instance.ITO.all()]
    items_detail = ", ".join(item_descriptions)

    title = ""
    description = ""

    if instance.order_status == 'Новый':
        title = f"Ваш заказ оформлен"
        description = f"{items_detail}"
    elif instance.order_status == 'Готов':
        title = f"Ваш заказ готов"
        description = f"{items_detail}"
    elif instance.order_status == 'Завершен':
        title = f"Вы закрыли счет"
        description = f"{items_detail}"

    if title and description and instance.customer:
        Notification.objects.create(
            title=title,
            description=description,
            recipient=instance.customer,
            status=instance.order_status
        )

        user_name = f"customer-{instance.customer.id}"

        channel_layer = get_channel_layer()  # Use this function
        async_to_sync(channel_layer.group_send)(
            user_name,
            {
                "type": "get_notifications_handler",
            }
        )

@receiver(post_save, sender=Order, dispatch_uid="order_waiter_status_changed")
def waiter_status_changed(sender, instance, created, **kwargs):
    logger.info(f"Signal received for order with id {instance.id}. Created: {created}")

    item_descriptions = [f"{item.menu_item.name} x {item.quantity}" for item in instance.ITO.all()]
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
        title = f"Бармен принял заказ"
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

        waiter_name = f"waiter-{instance.employee.id}"

        channel_layer = get_channel_layer()  # Use this function
        async_to_sync(channel_layer.group_send)(
            waiter_name,
            {
                "type": "get_notifications_handler",
            }
        )


admins = User.objects.filter(user_type="Admin")
    
@receiver(post_save, sender=Stock, dispatch_uid="storage_warning")
def storage_item_check(sender, instance, created, **kwargs):
    if instance.current_quantity <= instance.minimum_limit:

        for admin in admins:
            Notification.objects.create(
                title=f"Товар \"{instance.stock_item}\" заканчивается",
                description=f"Количество на складе: {instance.current_quantity} {instance.measurement_unit}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )
    

@receiver(post_save, sender=Branch, dispatch_uid="branch_created")
def branch_notification(sender, instance, created, **kwargs):
    if created:
        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новый филиал\"{instance.branch_name}\"",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=Branch, dispatch_uid="branch_deleted")
def branch_deleted_notification(sender, instance, **kwargs):
    for admin in admins:
        Notification.objects.create(
            title=f"Удалили филиал\"{instance.branch_name}\"",
            recipient=admin,
        )

        channel_layer = get_channel_layer()  # Use this function
        async_to_sync(channel_layer.group_send)(
            f"admin-{admin.id}",
            {
                "type": "get_notifications_handler",
            }
        )


@receiver(post_save, sender=Stock, dispatch_uid="storage_created")
def storage_item_created(sender, instance, created, **kwargs):
    if created and instance.type == "Сырье":

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новое сырье \"{instance.stock_item}\" ",
                description=f"Количество на складе: {instance.current_quantity} {instance.measurement_unit}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )

@receiver(post_delete, sender=Stock, dispatch_uid="storage_deleted")
def storage_item_deleted(sender, instance, **kwargs):
    if instance.type == "Сырье":

        for admin in admins:
            Notification.objects.create(
                title=f"Удалили сырье \"{instance.stock_item}\" ",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_save, sender=Menu_Item, dispatch_uid="menu_created")
def menu_item_created(sender, instance, created, **kwargs):
    if created:

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новую позицию\"{instance.name}\" ",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=Menu_Item, dispatch_uid="menu_deleted")
def menu_item_deleted(sender, instance, **kwargs):
    for admin in admins:
        Notification.objects.create(
            title=f"Удалили позицию\"{instance.name}\" ",
            recipient=admin,
        )

        channel_layer = get_channel_layer()  # Use this function
        async_to_sync(channel_layer.group_send)(
            f"admin-{admin.id}",
            {
                "type": "get_notifications_handler",
            }
        )


@receiver(post_save, sender=Stock, dispatch_uid="storage_ready_created")
def storage_ready_created(sender, instance, created, **kwargs):
    if created and instance.type == "Готовые продукты":

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили новую готовую продукцию \"{instance.stock_item}\" ",
                description=f"Количество на складе: {instance.current_quantity} {instance.measurement_unit}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=Stock, dispatch_uid="storage_ready_deleted")
def storage_ready_deleted(sender, instance, **kwargs):
    if instance.type == "Готовые продукты":

        for admin in admins:
            Notification.objects.create(
                title=f"Удалили готовую продукцию \"{instance.stock_item}\" ",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )
    
@receiver(post_save, sender=CustomUser, dispatch_uid="staff_created")
def staff_created(sender, instance, created, **kwargs):
    if created and instance.user_type == "Waiter" or "Bartender":

        for admin in admins:
            Notification.objects.create(
                title=f"Добавили {instance.first_name} как {instance.user_type}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


@receiver(post_delete, sender=CustomUser, dispatch_uid="staff_deleted")
def staff_deleted(sender, instance, **kwargs):
    if instance.user_type == "Waiter" or "Bartender":

        for admin in admins:
            Notification.objects.create(
                title=f"Удалили {instance.first_name} как {instance.user_type}",
                recipient=admin,
            )

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                f"admin-{admin.id}",
                {
                    "type": "get_notifications_handler",
                }
            )


bartenders = User.objects.filter(user_type="Bartender")


@receiver(post_save, sender=Order, dispatch_uid="order_bartender_status_accept")
def bartender_status_accept(sender, instance, created, **kwargs):
    logger.info(f"Signal received for order with id {instance.id}. Created: {created}")

    item_descriptions = [f"{item.menu_item.name} x {item.quantity}" for item in instance.ITO.all()]
    items_detail = ", ".join(item_descriptions)

    title = ""
    description = ""

    if instance.order_status == 'Новый':
        for bartender in bartenders:
            if bartender.branch == instance.branch:
                if instance.order_status == 'На вынос':
                    title = f"{instance.order_status} {instance.id}"
                    description = f"{items_detail}"
                elif instance.order_status == 'В заведении':
                    title = f"{instance.order_status} {instance.id}"
                    description = f"{items_detail}"

            if title and description and instance.employee:
                Notification.objects.create(
                    title=title,
                    description=description,
                    recipient=bartender,
                    status=instance.order_status
                )

            bartender_name = f"bartender-{bartender.id}"

            channel_layer = get_channel_layer()  # Use this function
            async_to_sync(channel_layer.group_send)(
                bartender_name,
                {
                    "type": "get_notifications_handler",
                }
            )