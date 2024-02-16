from rest_framework import serializers
from .models import Menu_Item, Category, Stock


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name',]
        model = Category


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'description', 'category',
                  'item_image', 'price_per_unit', 'branch',]
        model = Menu_Item


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'stock_item', 'current_quantity', 'measurement_unit',
                  'minimum_limit', 'type', 'restock_date', 'branch',]
        model = Stock
