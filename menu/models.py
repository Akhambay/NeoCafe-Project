from django.db import models
from django.utils.crypto import get_random_string
from users.models import Branch
from django.core.validators import MinLengthValidator
from django.core.validators import MinValueValidator

# ===========================================================================
# CATEGORY
# ===========================================================================


class Category(models.Model):
    name = models.CharField(max_length=100, default="Выпечка", validators=[
                            MinLengthValidator(3)])
    image = models.ImageField(
        upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['id']

# ===========================================================================
# STOCK ITEMS
# ===========================================================================


class Stock(models.Model):
    MEASUREMENT_UNIT_CHOICES = [
        ('гр', 'гр'),
        ('кг', 'кг'),
        ('мл', 'мл'),
        ('л', 'л'),
        ('шт', 'шт')
    ]

    TYPE_CHOICES = [
        ('Готовое', 'Готовое изделие'),
        ('Сырье', 'Сырье'),
    ]

    stock_item = models.CharField(max_length=225)
    current_quantity = models.IntegerField()
    measurement_unit = models.CharField(
        max_length=15, choices=MEASUREMENT_UNIT_CHOICES)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    minimum_limit = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(0)])
    restock_date = models.DateTimeField(auto_now_add=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='stocks')
    is_enough = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.stock_item}"


# ===========================================================================
# MENU ITEM
# ===========================================================================


class Menu_Item(models.Model):
    name = models.CharField(max_length=225)
    description = models.TextField(max_length=250, null=True, blank=True)
    category = models.ForeignKey(
        Category, related_name='menu_items', on_delete=models.CASCADE, default="Выпечка")
    item_image = models.ImageField(null=True, blank=True,
                                   upload_to='branch_images/')
    price_per_unit = models.PositiveIntegerField(default=100)
    branch = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

# ===========================================================================
# INGREDIENTS
# ===========================================================================


class Ingredient(models.Model):
    MEASUREMENT_UNIT_CHOICES = [
        ('гр', 'гр'),
        ('кг', 'кг'),
        ('мл', 'мл'),
        ('л', 'л'),
        ('шт', 'шт')
    ]

    menu_item = models.ForeignKey(
        Menu_Item, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=225)
    quantity = models.PositiveIntegerField()
    measurement_unit = models.CharField(
        max_length=15, choices=MEASUREMENT_UNIT_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.quantity}{self.measurement_unit})"


class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(Menu_Item, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient.name} ({self.quantity})"

# class ExtraItem(models.Model):
#     MILK = 'Молоко'
#     SYRUP = 'Сироп'
#     TYPE_CHOICES = [
#         (MILK, 'Молоко'),
#         (SYRUP, 'Сиропы')
#     ]

#     choice_category = models.ForeignKey(
#         Category, on_delete=models.CASCADE, related_name="extra_products", null=True
#     )
#     type_extra_product = models.CharField(
#         max_length=20, choices=TYPE_CHOICES, null=True, verbose_name="Доп. Продукт"
#     )
#     name = models.CharField(max_length=100, unique=True, verbose_name="Название доп. продукта")
#     quantity = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["name"]
#         verbose_name_plural = "Доп. Продукты"

#     def __str__(self):
#         return self.name