from django.db import models
from users.models import CustomUser


class Notification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    read = models.BooleanField(default=False)

    recipient = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE)
    position = models.CharField(max_length=20, blank=True)  # Assuming position is related to the user

    def __str__(self):
        return f"{self.title} - {self.status}"