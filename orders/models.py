from django.db import models
from menu.models import Menu_Item
from django.contrib.auth.models import User

# ===========================================================================
# TABLE
# ===========================================================================


class Table(models.Model):
    status_choice = (
        ('Reserved', 'Reserved'),
        ('Available', 'Available')
    )

    table_number = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20, choices=status_choice, default='Reserved')

    def __str__(self):
        return self.table_number


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
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Ready', 'Ready'),
        ('Cancelled', 'Cancelled'),
        ('Done', 'Done'),
    )

    order_type_choice = (
        ('In Venue', 'In Venue'),
        ('Takeaway', 'Takeaway')
    )

    status = models.CharField(
        max_length=20,
        choices=status_choice,
        default="New"
    )

    order_type = models.CharField(
        max_length=20,
        choices=order_type_choice
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    customer = models.ForeignKey(
        'users.CustomerProfile', on_delete=models.CASCADE, related_name='orders', null=True)

    total_price = models.PositiveIntegerField(default=0)
    table = models.ForeignKey(
        Table, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(
        'users.Profile', on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(
        'users.Branch', on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Order #{self.pk} - {self.order_type} - {self.status}"


class ItemToOrder(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='ITO')
    item = models.ForeignKey(Menu_Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
