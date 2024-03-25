from decimal import Decimal
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import Order, ItemToOrder, Table
from users.models import Profile, WaiterProfile, BartenderProfile
from menu.models import Menu_Item, Stock
from menu.serializers import MenuItemSerializer
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        orders = instance.order_set.all()
        for order in orders:
            if order.order_status in ['Новый', 'В процессе', 'Готов']:
                representation['is_available'] = False
                break
            else:
                representation['is_available'] = True
        return representation


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


"""
На вынос - новый, в процессе, завершен, отменен.
В заведении - Новый, В процессе, Готов, завершен, отменен.
бизнес логика такая - когда бармен приготовил заказ в заведении - официанту пришло уведомление о статусе «готово» = можно забирать заказ с бара и относить клиентам.
официант уже сам заказ закрывает после оплаты = переводит в статус завершено.
"""


class OrderSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(read_only=True, default="Новый")
    total_sum = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    table = TableSerializer()
    created_at = serializers.TimeField(required=False)
    updated_at = serializers.TimeField(required=False)
    completed_at = serializers.TimeField(allow_null=True, required=False)
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'table', 'order_status',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'employee_profile', 'ITO']

    def get_employee_profile(self, obj):
        from users.serializers import WaiterProfileSerializer, BartenderProfileSerializer
        if obj.employee:
            if obj.employee.user_type == 'Waiter':
                waiter_profile = WaiterProfile.objects.filter(
                    user=obj.employee).first()
                if waiter_profile:
                    return WaiterProfileSerializer(waiter_profile).data
            elif obj.employee.user_type == 'Bartender':
                bartender_profile = BartenderProfile.objects.filter(
                    user=obj.employee).first()
                if bartender_profile:
                    return BartenderProfileSerializer(bartender_profile).data

        return None

    def create(self, validated_data):
        ito_data = validated_data.pop('ITO', None)
        table_data = validated_data.pop('table', None)

        # Get the authenticated user
        authenticated_user = self.context['request'].user

        if table_data:
            table_number = table_data.get('table_number')
            branch_id = table_data.get('branch')

            table, _ = Table.objects.get_or_create(
                table_number=table_number, branch_id=branch_id, defaults={'is_available': False})

            validated_data['table'] = table

        order = Order.objects.create(
            employee=authenticated_user, **validated_data)

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
        # Update basic order information
        instance.order_status = validated_data.get(
            'order_status', instance.order_status)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.order_type = validated_data.get(
            'order_type', instance.order_type)
        instance.employee = validated_data.get('employee', instance.employee)
        instance.order_number = validated_data.get(
            'order_number', instance.order_number)

        # Update or delete items in the order
        ito_data = validated_data.pop('ITO', [])
        existing_ito_items = {
            ito_item.id: ito_item for ito_item in instance.ITO.all()}

        # Collect data for stock quantity validation
        available_to_order = []
        stock_quantity = []
        order_quantity = []
        ingredients_in_stock = True

        for ito_item_data in ito_data:
            ito_item_id = ito_item_data.get('id')
            ito_item_quantity = ito_item_data.get('quantity')

            if ito_item_id:
                # Update existing ItemToOrder instance
                ito_item_instance = existing_ito_items.pop(ito_item_id, None)
                if ito_item_instance:
                    ito_item_instance.quantity = ito_item_quantity
                    ito_item_instance.save()
                else:
                    raise serializers.ValidationError(
                        f"Item with id {ito_item_id} does not exist in this order.")
            else:
                # Create new ItemToOrder instance
                ito_item_instance = ItemToOrder.objects.create(
                    order=instance, **ito_item_data)

            # Collect data for stock quantity validation
            for ingredient in ito_item_instance.item.ingredients.all():
                stock_item = Stock.objects.filter(
                    branch=instance.branch, stock_item=ingredient.name).first()
                if stock_item:
                    available_quantity = stock_item.current_quantity // ingredient.quantity
                    available_to_order.append(available_quantity)
                    stock_quantity.append(stock_item.current_quantity)
                    order_quantity.append(ingredient.quantity)

                    required_quantity = ito_item_quantity * ingredient.quantity

                    # Check if stock is enough for the required quantity
                    if stock_item.current_quantity < required_quantity:
                        ingredients_in_stock = False
                        break

        # If all ingredients are enough in stock, subtract ingredients from stock
        if instance.order_status == "В процессе" and ingredients_in_stock:
            for ito_item_data in ito_data:
                for ingredient in ito_item_instance.item.ingredients.all():
                    stock_item = Stock.objects.filter(
                        branch=instance.branch, stock_item=ingredient.name).first()
                    if stock_item:
                        required_quantity = ito_item_quantity * ingredient.quantity
                        stock_item.current_quantity -= required_quantity
                        stock_item.save()

        # Delete any remaining ItemToOrder instances (if any)
        for ito_item_instance in existing_ito_items.values():
            ito_item_instance.delete()

        # Update total sum
        instance.total_sum = self.get_total_sum(instance)

        if instance.order_status == "Завершен":
            instance.completed_at = timezone.now()

        # Save the changes to the Order instance
        instance.save()

        return instance

    def get_total_sum(self, obj):
        total_sum = 0
        for ito in obj.ITO.all():
            total_sum += ito.item.price_per_unit * ito.quantity
        return total_sum


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class TableDetailedSerializer(serializers.ModelSerializer):
    order_set = OrderSerializer(many=True)

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_available', 'order_set']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        orders = instance.order_set.all()
        for order in orders:
            if order.order_status in ['Новый', 'В процессе', 'Готов']:
                representation['is_available'] = False
                break
            else:
                representation['is_available'] = True
        return representation

    def create(self, validated_data):
        order_data = validated_data.pop('order_set')
        table = Table.objects.create(**validated_data)
        for order in order_data:
            Order.objects.create(table=table, **order)
        return table


# ================================================================
# ORDER ONLINE
# ================================================================


class OrderOnlineSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(read_only=True, default="Новый")
    total_sum = serializers.SerializerMethodField()
    bonus_points = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    created_at = TimeField()
    updated_at = TimeField()
    completed_at = TimeField(allow_null=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'order_status',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'customer', 'bonus_points', 'ITO']

    def create(self, validated_data):
        ito_data = validated_data.pop('ITO', None)

        order = Order.objects.create(**validated_data)

        for ito in ito_data:
            ItemToOrder.objects.create(order=order, **ito)

        return order

    def update(self, instance, validated_data):
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


class OrderOnlineDetailedSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(default="Новый")
    total_sum = serializers.SerializerMethodField()
    bonus_points = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    created_at = TimeField(required=False)
    updated_at = TimeField(required=False)
    completed_at = TimeField(allow_null=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'order_status',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'customer', 'bonus_points', 'ITO']

    def update(self, instance, validated_data):
        # Update basic order information
        instance.order_status = validated_data.get(
            'order_status', instance.order_status)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.order_type = validated_data.get(
            'order_type', instance.order_type)
        instance.customer = validated_data.get('customer', instance.customer)
        instance.order_number = validated_data.get(
            'order_number', instance.order_number)

        # Update or delete items in the order
        ito_data = validated_data.pop('ITO', [])
        existing_ito_items = {
            ito_item.id: ito_item for ito_item in instance.ITO.all()}

        # Collect data for stock quantity validation
        available_to_order = []
        stock_quantity = []
        order_quantity = []
        ingredients_in_stock = True

        for ito_item_data in ito_data:
            ito_item_id = ito_item_data.get('id')
            ito_item_quantity = ito_item_data.get('quantity')

            if ito_item_id:
                # Update existing ItemToOrder instance
                ito_item_instance = existing_ito_items.pop(ito_item_id, None)
                if ito_item_instance:
                    ito_item_instance.quantity = ito_item_quantity
                    ito_item_instance.save()
                else:
                    raise serializers.ValidationError(
                        f"Item with id {ito_item_id} does not exist in this order.")
            else:
                # Create new ItemToOrder instance
                ito_item_instance = ItemToOrder.objects.create(
                    order=instance, **ito_item_data)

            # Collect data for stock quantity validation
            for ingredient in ito_item_instance.item.ingredients.all():
                stock_item = Stock.objects.filter(
                    branch=instance.branch, stock_item=ingredient.name).first()
                if stock_item:
                    available_quantity = stock_item.current_quantity // ingredient.quantity
                    available_to_order.append(available_quantity)
                    stock_quantity.append(stock_item.current_quantity)
                    order_quantity.append(ingredient.quantity)

                    required_quantity = ito_item_quantity * ingredient.quantity

                    # Check if stock is enough for the required quantity
                    if stock_item.current_quantity < required_quantity:
                        ingredients_in_stock = False
                        break

        # If all ingredients are enough in stock, subtract ingredients from stock
        if instance.order_status == "В процессе" and ingredients_in_stock:
            for ito_item_data in ito_data:
                for ingredient in ito_item_instance.item.ingredients.all():
                    stock_item = Stock.objects.filter(
                        branch=instance.branch, stock_item=ingredient.name).first()
                    if stock_item:
                        required_quantity = ito_item_quantity * ingredient.quantity
                        stock_item.current_quantity -= required_quantity
                        stock_item.save()

        # Delete any remaining ItemToOrder instances (if any)
        for ito_item_instance in existing_ito_items.values():
            ito_item_instance.delete()

        # Update total sum and bonus points
        instance.total_sum = self.get_total_sum(instance)
        instance.bonus_points = self.get_bonus_points(instance.total_sum)

        if instance.order_status == "Завершен":
            instance.completed_at = timezone.now()

        # Save the changes to the Order instance
        instance.save()

        return instance

    def get_total_sum(self, obj):
        total_sum = 0
        for ito in obj.ITO.all():
            total_sum += ito.item.price_per_unit * ito.quantity
        return total_sum

    def get_bonus_points(self, total_sum):
        return Decimal(total_sum) * Decimal('0.10')


class CustomerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


# ===========================================================================
# MTO
# ===========================================================================


class CloseOrderSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=(('closed', 'closed')))
    guest_money = serializers.IntegerField(min_value=0)
