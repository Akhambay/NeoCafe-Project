from django.db import models
from users.models import Branch, CustomUser
from menu.models import Menu_Item
from django.utils.translation import gettext_lazy as _

# ===========================================================================
# TABLE
# ===========================================================================


class Table(models.Model):
    class TableStatus(models.TextChoices):
        OCCUPIED = 'occupied', _('Occupied')
        AVAILABLE = 'available', _('Available')

    table_number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=TableStatus.choices,
        default=TableStatus.AVAILABLE
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='orders', blank=True, null=True)


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
    class OrderStatus(models.TextChoices):
        NEW = 'new', _('New')
        IN_PROGRESS = 'in_progress', _('In Progress')
        READY = 'ready', _('Ready')
        CANCELLED = 'cancelled', _('Cancelled'),
        DONE = 'done', _('Done')

    class OrderType(models.TextChoices):
        IN_VENUE = 'in_venue', _('In Venue')
        TAKEAWAY = 'takeaway', _('Takeaway')

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW
    )

    order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    customer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='orders'
    )

    table = models.ForeignKey(
        Table, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(Menu_Item, through='OrderedItem')
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Order #{self.pk} - {self.order_type} - {self.status}"


class OrderedItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Menu_Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()  # Add a price field here

    def total_price(self):
        return self.quantity * self.price
