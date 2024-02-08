from django.db import models
from django.utils.crypto import get_random_string
from users.models import Branch


class Category(models.Model):
    name = models.CharField(max_length=255, default="Выпечка")
    image = models.ImageField(null=True, blank=True,
                              upload_to='category_images/')

    def __str__(self):
        return f"{self.name}"


class Menu_Item(models.Model):
    TYPE_CHOICES = [
        ('product', 'Product'),
        ('material', 'Material'),
    ]

    name = models.CharField(max_length=255, default="Выпечка")
    description = models.TextField(max_length=250, null=True, blank=True)
    category = models.ForeignKey(
        Category, related_name='menu_items', on_delete=models.CASCADE, default="Выпечка")
    image = models.ImageField(null=True, blank=True,
                              upload_to='branch_images/')
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    price_per_unit = models.PositiveIntegerField(default=100)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='menu_items', blank=True, null=True
    )

    def __str__(self):
        return f"{self.name}"
