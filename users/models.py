from django.contrib.auth.models import AbstractUser
from django.db import models


class Schedule(models.Model):
    DAYS_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    working_days = models.CharField(max_length=15, choices=DAYS_CHOICES)
    start_time = models.TimeField(max_length=15)
    end_time = models.TimeField(max_length=15)


class Branch(models.Model):
    branch_name = models.CharField(max_length=250)
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(null=True, blank=True,
                              upload_to='branch_images/')
    description = models.TextField(blank=True)
    link_2gis = models.CharField(max_length=15)
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name='branch_schedule')

    def __str__(self):
        return self.branch_name


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('waiter', 'Waiter'),
        ('bartender', 'Bartender'),
        ('customer', 'Customer'),
    ]

    first_name = models.CharField(null=True, blank=True, max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    DOB = models.DateField(null=True, blank=True, verbose_name='Date of Birth')
    phone_number = models.CharField(null=True, blank=True, unique=True,
                                    help_text='Contact phone number', max_length=15)
    email = models.EmailField(max_length=30, unique=True)
    avatar = models.ImageField(
        null=True, blank=True, default='/profile_pics/default.png', upload_to='profile_pics/')
    bonus_points = models.PositiveIntegerField(default=0)
    confirmation_code = models.CharField(
        max_length=4, blank=True, null=True, verbose_name='Confirmation Code')
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='branch')
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_type})"
