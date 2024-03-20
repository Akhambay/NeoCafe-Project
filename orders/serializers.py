from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import Order, ItemToOrder, Table
from users.models import Profile
from menu.models import Menu_Item, Stock
from menu.serializers import MenuItemSerializer
# from users.serializers import EmployeeProfileSerializer
from django.utils import timezone
from django.db import transaction
from datetime import datetime


class ItemToOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    total_price = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()

    class Meta:
        model = ItemToOrder
        fields = ['id', 'item', 'item_name', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.item.price_per_unit * obj.quantity

    def get_item_name(self, obj):
        return obj.item.name


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_available', 'branch']

    """def create(self, validated_data):
        order_data = validated_data.pop('order_set')
        table = Table.objects.create(**validated_data)
        for order in order_data:
            Order.objects.create(table=table, **order)
        return table"""


class TimeField(serializers.Field):
    def to_representation(self, value):
        if value is None:
            return None
        return value.strftime('%H:%M')

    def to_internal_value(self, data):
        try:
            return datetime.strptime(data, '%H:%M').time()
        except ValueError:
            raise serializers.ValidationError(
                "Invalid time format. Use HH:MM format.")


class OrderSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(read_only=True, default="Новый")
    total_sum = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    table = TableSerializer()
    created_at = TimeField()
    updated_at = TimeField()
    completed_at = TimeField(allow_null=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'table', 'order_status',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'employee', 'ITO']

    def create(self, validated_data):
        ito_data = validated_data.pop('ITO', None)
        table_data = validated_data.pop('table', None)

        if table_data:
            table_number = table_data.get('table_number')
            branch_id = table_data.get('branch')

            table, _ = Table.objects.get_or_create(
                table_number=table_number, branch_id=branch_id, defaults={'is_available': False})

            validated_data['table'] = table

        order = Order.objects.create(**validated_data)

        for ito in ito_data:
            ItemToOrder.objects.create(order=order, **ito)

        return order

    def update(self, instance, validated_data):
        instance.table = validated_data.get('table', instance.table)
        instance.save()
        ito_data = validated_data.get('ITO')
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
            total_price = ito.item.price_per_unit * ito.quantity
            total_sum += total_price
        obj.save()
        return total_sum


class OrderDetailedSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(default="Новый")
    total_sum = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    created_at = TimeField(required=False)
    updated_at = TimeField(required=False)
    completed_at = TimeField(allow_null=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'table', 'order_status',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'employee', 'ITO']

    def update(self, instance, validated_data):
        instance.order_status = validated_data.get(
            'order_status', instance.order_status)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.order_type = validated_data.get(
            'order_type', instance.order_type)
        instance.employee = validated_data.get('employee', instance.employee)

        # Update nested serializer data
        ito_data = validated_data.pop('ITO', [])
        for ito_item_data in ito_data:
            ito_item_id = ito_item_data.get('id')
            ito_item_quantity = ito_item_data.get('quantity')

            # Retrieve the ItemToOrder instance or create a new one if it doesn't exist
            ito_item, _ = ItemToOrder.objects.get_or_create(
                id=ito_item_id, defaults={'order': instance})
            ito_item.quantity = ito_item_quantity
            ito_item.save()

            # Deduct ingredients from stock if order status is 'In Progress'
            if instance.order_status == "В процессе":
                for ingredient in ito_item.item.ingredients.all():
                    stock_item = Stock.objects.filter(
                        branch=instance.branch, stock_item=ingredient.name).first()
                    ingredient_quantity = ingredient.quantity
                    if stock_item:
                        stock_item.current_quantity -= ito_item_quantity * ingredient_quantity

                        stock_item.save()

                        # Ensure stock is not negative
                        if stock_item.current_quantity < 0:
                            raise serializers.ValidationError(
                                f"Insufficient stock for ingredient {ingredient.name}")

        if instance.order_status == "Завершен":
            instance.completed_at = timezone.now()

        # Save the changes to the Order instance
        instance.save()

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


class TableDetailedSerializer(serializers.ModelSerializer):
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
    created_at = serializers.DateTimeField(format='%H:%M')
    updated_at = serializers.DateTimeField(format='%H:%M')
    completed_at = serializers.DateTimeField(format='%H:%M')

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'total_price', 'status', 'customer',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'ITO']
        read_only_fields = ['order_number',
                            'status', 'total_price', 'total_sum']

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
