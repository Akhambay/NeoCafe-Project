from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import Order, ItemToOrder, Table
from users.models import Profile
from menu.models import Menu_Item
from menu.serializers import MenuItemSerializer
# from users.serializers import EmployeeProfileSerializer


class ItemToOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = ItemToOrder
        fields = ['id', 'item', 'quantity', ]
        # order


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['table_number', 'is_available']

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
    ITO = ItemToOrderSerializer(many=True)
    table = TableSerializer()

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'table', 'status',
                  'created_at', 'customer', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'employee', 'ITO']

    def create(self, validated_data):
        ito_data = validated_data.pop('ITO')
        table_data = validated_data.pop('table', None)
        order = Order.objects.create(**validated_data)

        for ito in ito_data:
            drop_id = ito.pop('id')
            ItemToOrder.objects.create(order=order, **ito)

        if table_data:
            table_number = table_data.get('table_number', 1)
            # Provide a default status if not provided
            status = table_data.get('status', 'Reserved')
            table, _ = Table.objects.get_or_create(
                table_number=table_number, defaults={'status': status})

            order.table = table
            order.save()

        return order

    def update(self, instance, validated_data):
        instance.table = validated_data.get('table', instance.table)
        instance.save()
        ito_data = validated_data.get('ItemToOrder')
        for ito in ito_data:
            ito_instance = ItemToOrder.objects.get(
                id=ito.get('id'))
            ito_instance.item = ito.get('item', ito_instance.item)
            ito_instance.quantity = ito.get(
                'quantity', ito_instance.quantity)
            ito_instance.save()
        return instance

    def get_total_sum(self, obj):
        total_sum = 0
        for ito in obj.ITO.all():
            total_sum += ito.item.price_per_unit * ito.quantity
        obj.total_price = total_sum
        obj.save()
        return total_sum
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class TableDetailSerializer(serializers.ModelSerializer):
    order_set = OrderSerializer(many=True)

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_available', 'order_set']

    def create(self, validated_data):
        order_data = validated_data.pop('order_set')
        table = Table.objects.create(**validated_data)
        for order in order_data:
            Order.objects.create(table=table, **order)
        return table


class OrderOnlineSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    total_price = serializers.IntegerField(min_value=0, read_only=True)
    total_sum = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'customer',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'ITO']
        read_only_fields = ['status', 'total_price', 'total_sum']

    def create(self, validated_data):
        ito_data = validated_data.pop('ITO', [])
        customer = validated_data.pop('customer', None)

        # Assuming 'customer' is a CustomerProfile instance, not just the customer ID.
        order = Order.objects.create(customer=customer, **validated_data)

        for ito in ito_data:
            ito.pop('id', None)
            ItemToOrder.objects.create(order=order, **ito)

        return order

    def update(self, instance, validated_data):
        ito_data = validated_data.get('ITO', [])

        for ito in ito_data:
            ito_instance = ItemToOrder.objects.get(id=ito.get('id'))
            ito_instance.item = ito.get('item', ito_instance.item)
            ito_instance.quantity = ito.get('quantity', ito_instance.quantity)
            ito_instance.save()

        return instance

    def get_total_sum(self, obj):
        total_sum = 0
        for ito in obj.ITO.all():
            total_sum += ito.item.price_per_unit * ito.quantity
        obj.total_price = total_sum
        obj.save()
        return total_sum


class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class TableDetailSerializer(serializers.ModelSerializer):
    order_set = OrderSerializer(many=True)

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'status', 'order_set']

    def create(self, validated_data):
        order_data = validated_data.pop('order_set')
        table = Table.objects.create(**validated_data)
        for order in order_data:
            Order.objects.create(table=table, **order)
        return table

# ===========================================================================
# MTO
# ===========================================================================


class CloseOrderSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=(('closed', 'closed')))
    guest_money = serializers.IntegerField(min_value=0)
