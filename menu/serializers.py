from rest_framework import serializers
from .models import Menu_Item, Category, Stock, Ingredient


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name',]
        model = Category


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'description', 'category',
                  'item_image', 'price_per_unit', 'branch',]
        model = Menu_Item


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'current_quantity', 'measurement_unit',
                  'minimum_limit', 'type', 'restock_date', 'branch',]
        model = Ingredient


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['menu_item', 'ingredient', 'current_quantity',
                  'minimum_quantity', 'restock_date', 'is_enough',]
        model = Stock
