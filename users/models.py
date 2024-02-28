from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# ===========================================================================
# BRANCH SCHEDULE
# ===========================================================================


class Schedule(models.Model):
    DAYS_CHOICES = [
        ('Пн', _('Пн')),
        ('Вт', _('Вт')),
        ('Ср', _('Ср')),
        ('Чт', _('Чт')),
        ('Пт', _('Пт')),
        ('Сб', _('Сб')),
        ('Вс', _('Вс')),
    ]

    branch = models.ForeignKey(
        'Branch', on_delete=models.CASCADE, related_name='schedules', null=True)
    day = models.CharField(max_length=10, choices=DAYS_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_display()}: {self.start_time} - {self.end_time}"

# ===========================================================================
# EMPLOYEE SCHEDULE
# ===========================================================================


class EmployeeSchedule(models.Model):
    DAYS_CHOICES = [
        ('Пн', _('Пн')),
        ('Вт', _('Вт')),
        ('Ср', _('Ср')),
        ('Чт', _('Чт')),
        ('Пт', _('Пт')),
        ('Сб', _('Сб')),
        ('Вс', _('Вс')),
    ]

    employee = models.ForeignKey(
        'CustomUser', on_delete=models.CASCADE, related_name='employee_schedules', null=True)
    day = models.CharField(max_length=10, choices=DAYS_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_display()}: {self.start_time} - {self.end_time}"

# ===========================================================================
# BRANCH
# ===========================================================================


class Branch(models.Model):
    branch_name = models.CharField(max_length=250)
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(null=True, blank=True,
                              upload_to='branch_images/')
    description = models.TextField(blank=True)
    link_2gis = models.CharField(max_length=100)
    table_quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.branch_name

# ===========================================================================
# CUSTOM USER MANAGER
# ===========================================================================


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        # Save user first
        user.save(using=self._db)

        # Set default values for refresh and access tokens
        refresh = RefreshToken.for_user(user)
        extra_fields['refresh_token'] = str(refresh)
        extra_fields['access_token'] = str(refresh.access_token)

        # Save again after setting bonus_points and access_token
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# ===========================================================================
# CUSTOM USER
# ===========================================================================


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('Waiter', 'Waiter'),
        ('Bartender', 'Bartender'),

    ]

    first_name = models.CharField(null=True, blank=True, max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)
    user_type = models.CharField(
        max_length=50, choices=USER_TYPE_CHOICES, default='Waiter')

    email = models.EmailField(
        max_length=30, unique=True, null=True)
    bonus_points = models.PositiveIntegerField(default=0)
    confirmation_code = models.CharField(
        max_length=4, blank=True, null=True, verbose_name='Confirmation Code')
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='employees', blank=True, null=True)
    is_staff = models.BooleanField(default=True)
    orders = models.ManyToManyField(
        'orders.Order', related_name='orders', blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ===========================================================================
# PROFILES
# ===========================================================================


class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('Waiter', 'Waiter'),
        ('Bartender', 'Bartender'),
        # Add more user types as needed
    ]

    user = models.OneToOneField(
        CustomUser, related_name='profile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    user_type = models.CharField(
        max_length=50, choices=USER_TYPE_CHOICES, default='Waiter')
    schedule = models.ForeignKey(
        EmployeeSchedule, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class WaiterProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name='waiterprofile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    schedule = models.ForeignKey(
        EmployeeSchedule, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class BartenderProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name='bartenderprofile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    schedule = models.ForeignKey(
        EmployeeSchedule, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CustomerProfile(models.Model):
    customer = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50)
    orders = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL, blank=True, null=True)
    bonus = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.email
