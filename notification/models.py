from django.db import models
from menu.models import Branch
from orders.models import Order, Table
from users.models import CustomUser


class Notification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    read = models.BooleanField(default=False)
    table = models.ForeignKey(Table, blank=True, null=True, on_delete=models.SET_NULL)
    recipient = models.ForeignKey(CustomUser, related_name='recipient_name', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.status}"