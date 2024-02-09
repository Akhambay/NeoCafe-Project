from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


class Schedule(models.Model):
    DAYS_CHOICES = [
        ('ПН', 'Понедельник'),
        ('ВТ', 'Вторник'),
        ('СР', 'Среда'),
        ('ЧТ', 'Четверг'),
        ('ПТ', 'Пятница'),
        ('СБ', 'Суббота'),
        ('ВС', 'Воскресенье'),
    ]

    # employee = models.ForeignKey(
    #   'CustomUser', on_delete=models.CASCADE, related_name='employee_schedules')
    working_days = models.CharField(max_length=15, choices=DAYS_CHOICES)
    start_time = models.TimeField(max_length=15)
    end_time = models.TimeField(max_length=15)

    def __str__(self):
        return f"{self.working_days}: {self.start_time} - {self.end_time}"


class Branch(models.Model):
    branch_name = models.CharField(max_length=250)
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(null=True, blank=True,
                              upload_to='branch_images/')
    description = models.TextField(blank=True)
    link_2gis = models.CharField(max_length=100)
    schedule = models.ManyToManyField(
        Schedule, related_name='branches_schedule', related_query_name='branch_schedule', blank=True,
    )
    table_quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.branch_name


class BranchSchedule(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        refresh = RefreshToken.for_user(user)
        extra_fields['refresh_token'] = str(refresh)
        extra_fields['access_token'] = str(refresh.access_token)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('username'):
            extra_fields['username'] = self.generate_unique_username(email)
        return self.create_user(email, password, **extra_fields)

    def generate_unique_username(self, email):
        username_prefix = email.split('@')[0]

    # Generate a random string to ensure uniqueness
        random_suffix = get_random_string(length=4)

        unique_username = f"{username_prefix}_{random_suffix}"

        return unique_username


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('waiter', 'Waiter'),
        ('bartender', 'Bartender'),
    ]

    first_name = models.CharField(null=True, blank=True, max_length=50)
    last_name = models.CharField(null=True, blank=True, max_length=50)
    user_type = models.CharField(
        max_length=50, choices=USER_TYPE_CHOICES, default='admin')

    email = models.EmailField(
        max_length=30, unique=True, null=True)
    bonus_points = models.PositiveIntegerField(default=0)
    confirmation_code = models.CharField(
        max_length=4, blank=True, null=True, verbose_name='Confirmation Code')
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='employees', blank=True, null=True)
    schedule = models.ManyToManyField(
        Schedule, related_name='employees_schedule', related_query_name='employee_schedule', blank=True,
    )
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} {self.first_name} ({self.user_type})"


class Customer(CustomUser):
    pass
