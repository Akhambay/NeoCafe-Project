from django.db import models
from django.utils.crypto import get_random_string
from users.models import Branch


class Category(models.Model):
    name = models.CharField(max_length=255, default="Выпечка")

    def __str__(self):
        return f"{self.name}"


class Menu_Item(models.Model):
    name = models.CharField(max_length=255, default="Выпечка")
    description = models.TextField(max_length=250, null=True, blank=True)
    category = models.ForeignKey(
        Category, related_name='menu_items', on_delete=models.CASCADE, default="Выпечка")
    item_image = models.ImageField(null=True, blank=True,
                                   upload_to='branch_images/')
    price_per_unit = models.PositiveIntegerField(default=100)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='menu_items', blank=True, null=True
    )

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    MEASUREMENT_UNIT_CHOICES = [
        ('гр', 'Грамм'),
        ('кг', 'Килограмм'),
        ('мл', 'мл'),
        ('литр', 'Литр'),
        ('шт', 'Штук')
    ]

    TYPE_CHOICES = [
        ('готовое', 'Готовое изделие'),
        ('сырье', 'Сырье'),
    ]

    name = models.CharField(max_length=255, default="Выпечка")
    description = models.TextField(max_length=250, null=True, blank=True)
    current_quantity = models.PositiveIntegerField(default=100)
    measurement_unit = models.CharField(
        max_length=15, choices=MEASUREMENT_UNIT_CHOICES)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    minimum_limit = models.PositiveIntegerField(default=10)
    restock_date = models.DateTimeField(auto_now_add=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='ingredients', blank=True, null=True
    )

    def __str__(self):
        return f"{self.name}"
