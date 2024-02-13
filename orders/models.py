from django.db import models
from users.models import Branch, CustomUser
from django.utils.translation import gettext_lazy as _


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


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        NEW = 'new', _('New')
        IN_PROGRESS = 'in_progress', _('In Progress')
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

    cart_id = models.IntegerField(null=True, blank=True)
    customer_email = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='order_customer'
    )

    table = models.ForeignKey(
        Table, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.order_type} - {self.status}"
