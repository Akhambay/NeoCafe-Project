from django.db import transaction
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
    phone_number = models.CharField(max_length=20)
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
    def create_user(self, email, password=None, user_type='Официант', **extra_fields):
        with transaction.atomic():
            if not email:
                raise ValueError('The Email field must be set')
            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)

            # Create a profile for the user
            if user_type == 'Официант':
                WaiterProfile.objects.create(user=user)
            elif user_type == 'Бармен':
                BartenderProfile.objects.create(user=user)
            elif user_type == 'Посетитель':
                CustomerProfile.objects.create(user=user)

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
        ('Официант', 'Официант'),
        ('Бармен', 'Бармен'),
        ('Посетитель', 'Посетитель'),
        ('Администратор', 'Администратор'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)
    user_type = models.CharField(
        max_length=50, choices=USER_TYPE_CHOICES, default='Официант')

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

    @property
    def profile(self):
        # Access the related profile based on user_type
        if self.user_type == 'Официант':
            return self.waiterprofile
        elif self.user_type == 'Бармен':
            return self.bartenderprofile
        else:
            return None

    @property
    def waiterprofile(self):
        try:
            return self.waiterprofile
        except WaiterProfile.DoesNotExist:
            return None

    @property
    def bartenderprofile(self):
        try:
            return self.bartenderprofile
        except BartenderProfile.DoesNotExist:
            return None


# ===========================================================================
# PROFILES
# ===========================================================================
class Profile(models.Model):

    user = models.OneToOneField(
        CustomUser, related_name='profile', on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    user_type = models.CharField(
        max_length=50, default='Официант')
    schedule = models.ForeignKey(
        EmployeeSchedule, on_delete=models.SET_NULL, blank=True, null=True)
    branch = models.ForeignKey(
        Branch, related_name='profiles', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.user_type}"


class WaiterProfile(models.Model):

    user = models.OneToOneField(
        CustomUser, related_name='waiterprofile', on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    user_type = models.CharField(
        max_length=50, default='Официант')
    schedule = models.ForeignKey(
        EmployeeSchedule, on_delete=models.SET_NULL, blank=True, null=True)
    branch = models.ForeignKey(
        Branch, related_name='waiter_profiles', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.user_type}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name='customerprofile', on_delete=models.CASCADE, blank=True, null=True)
    user_type = models.CharField(
        max_length=50, default='Посетитель')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    orders = models.ForeignKey(
        "orders.Order", on_delete=models.SET_NULL, blank=True, null=True)

    bonus_points = models.PositiveIntegerField(default=100)

    def __str__(self):
        return f"{self.first_name} {self.user_type}"


class BartenderProfile(models.Model):

    user = models.OneToOneField(
        CustomUser, related_name='bartenderprofile', on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    user_type = models.CharField(
        max_length=50, default='Бармен')
    schedule = models.ForeignKey(
        EmployeeSchedule, on_delete=models.SET_NULL, blank=True, null=True)
    branch = models.ForeignKey(
        Branch, related_name='bartender_profiles', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.user_type}"
