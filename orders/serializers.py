from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import Order, OrderedItem, Table
from users.models import EmployeeProfile
from menu.models import Menu_Item
from menu.serializers import MenuItemSerializer
from users.serializers import EmployeeProfileSerializer


class OrderedItemSerializer(serializers.ModelSerializer):
    item = MenuItemSerializer()
    # id = serializers.IntegerField()

    class Meta:
        model = OrderedItem
        fields = ['id', 'item', 'quantity']


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


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'status']
        # branch


class TableDetailSerializer(serializers.ModelSerializer):
    order_set = OrderSerializer(many=True)

    class Meta:
        model = Table
        fields = ['id', 'status', 'order_set']

    def create(self, validated_data):
        order_data = validated_data.pop('order_set')
        table = Table.objects.create(**validated_data)
        for order in order_data:
            Order.objects.create(table=table, **order)
        return table


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    total_price = serializers.IntegerField(min_value=0, read_only=True)
    total_sum = serializers.SerializerMethodField()
    OrderedItems = OrderedItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'table', 'status',
                  'created_at', 'user_profile', 'total_sum', 'employee', 'items']

    def create(self, validated_data):
        ordereditems_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for ordereditem in ordereditems_data:
            drop_id = ordereditem.pop('id')
            OrderedItem.objects.create(order=order, **ordereditem)
        return order

    def update(self, instance, validated_data):
        instance.table = validated_data.get('table', instance.table)
        instance.save()
        ordereditems_data = validated_data.get('item')
        for ordereditem in ordereditems_data:
            ordereditem_instance = Menu_Item.objects.get(
                id=ordereditem.get('id'))
            ordereditem_instance.item = ordereditem.get(
                'item', ordereditem_instance.item)
            ordereditem_instance.quantity = ordereditem.get(
                'quantity', ordereditem_instance.quantity)
            ordereditem_instance.save()
        return instance

    def get_total_sum(self, obj):
        total_sum = 0
        for ordereditem in obj.OrderedItems.all():
            total_sum += ordereditem.meal.price * ordereditem.quantity
        obj.total_price = total_sum
        obj.save()
        return total_sum

# ===========================================================================
# MTO
# ===========================================================================


class CloseOrderSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=(('closed', 'closed')))
    guest_money = serializers.IntegerField(min_value=0)
