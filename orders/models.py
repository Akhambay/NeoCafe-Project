from django.db import models
from menu.models import Menu_Item, Branch, ExtraItem
from users.models import CustomUser
from django.contrib.auth.models import User

# ===========================================================================
# TABLE
# ===========================================================================


class Table(models.Model):
    table_number = models.PositiveIntegerField()
    is_available = models.BooleanField(default=False)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.table_number)  # Ensure to return a string


# ===========================================================================
# ORDER
# ===========================================================================
'''
На вынос - новый, в процессе, завершен, отменен.
В заведении - новый, в процессе, готов, завершен, отменен.
Когда бармен приготовил заказ в заведении - 
официанту пришло уведомление о статусе «Готово» = можно забирать заказ с бара и относить клиентам.
официант уже сам заказ закрывает после оплаты = переводит в статус завершено.
'''


class Order(models.Model):
    status_choice = (
        ('Новый', 'Новый'),
        ('В процессе', 'В процессе'),
        ('Готов', 'Готов'),
        ('Отменен', 'Отменен'),
        ('Завершен', 'Завершен'),
    )

    order_type_choice = (
        ('В заведении', 'В заведении'),
        ('На вынос', 'На вынос')
    )

    order_status = models.CharField(
        max_length=20,
        choices=status_choice,
        default="Новый"
    )

    order_type = models.CharField(
        max_length=20,
        choices=order_type_choice
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    customer = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, related_name='customer_orders', null=True)

    total_price = models.PositiveIntegerField(default=0)
    table = models.ForeignKey(
        Table, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, related_name='employee_orders', null=True)
    branch = models.ForeignKey(
        'users.Branch', on_delete=models.CASCADE, related_name='cart', null=True, blank=True)

    order_number = models.PositiveIntegerField(null=True, blank=True)
    bonus_points_to_subtract = models.PositiveIntegerField(
        null=True, blank=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.order_type} - {self.order_status}"

    def save(self, *args, **kwargs):
        if not self.pk:  # If the instance is being created
            # Get the latest order number
            last_order = Order.objects.order_by('-order_number').first()
            if last_order:
                last_order_number = last_order.order_number
            else:
                last_order_number = 3000  # Start from 3000 if no orders exist
            # Increment the order number
            self.order_number = last_order_number + 1
        super().save(*args, **kwargs)


class ItemToOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ITO')
    item = models.ForeignKey(Menu_Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    extra_product = models.ManyToManyField(
        ExtraItem,
        blank=True,
        related_name="extra_order",
    )


class OrderItemExtraProduct(models.Model):
    order_item = models.ForeignKey(ItemToOrder, on_delete=models.CASCADE)
    extra_product = models.ForeignKey(ExtraItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)