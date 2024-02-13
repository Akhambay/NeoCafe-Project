from rest_framework import serializers
from .models import Menu_Item, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name',]
        model = Category


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'description', 'category',
                  'item_image', 'price_per_unit', 'branch',]
        model = Menu_Item
