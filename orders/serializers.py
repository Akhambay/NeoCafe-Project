from rest_framework import serializers
from .models import Order, OrderedItem
from users.serializers import CustomUserSerializer, BranchSerializer
from menu.serializers import MenuItemSerializer


class OrderedItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer()

    class Meta:
        model = OrderedItem
        fields = ['item', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderedItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'order_type', 'created_at', 'updated_at', 'completed_at',
                  'customer', 'table', 'employee', 'branch', 'items']


class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
