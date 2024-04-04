from .models import Order
from decimal import Decimal
from rest_framework import serializers
from .models import Order, ItemToOrder, Table
from menu.models import Stock
from django.utils import timezone
from django.db import transaction
from datetime import datetime


"""
На вынос - новый, в процессе, завершен, отменен.
В заведении - Новый, В процессе, Готов, завершен, отменен.
бизнес логика такая - когда бармен приготовил заказ в заведении - официанту пришло уведомление о статусе «готово» = можно забирать заказ с бара и относить клиентам.
официант уже сам заказ закрывает после оплаты = переводит в статус завершено.
"""


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
        if isinstance(data, str):
            try:
                return datetime.strptime(data, '%H:%M').time()
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid time format. Use HH:MM format.")
        elif isinstance(data, datetime.time):
            return data.strftime('%H:%M')  # Convert time object to string
        else:
            raise serializers.ValidationError(
                "Invalid input format for time field.")


class OrderSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(read_only=True, default="Новый")
    total_sum = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    table = TableSerializer()
    created_at = TimeField(required=False, default=timezone.now)
    updated_at = TimeField(required=False, default=timezone.now)
    completed_at = TimeField(allow_null=True, required=False)
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'table', 'order_status',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'employee_profile', 'ITO']

    def get_employee_profile(self, instance):
        from users.models import CustomUser
        from users.serializers import CustomUserSerializer
        employee = instance.employee
        if employee:
            user_type = employee.user_type
            if user_type == 'Waiter':
                waiter_profile = CustomUser.objects.filter(
                    id=employee.id, user_type='Waiter').first()
                if waiter_profile:
                    return CustomUserSerializer(waiter_profile).data
            elif user_type == 'Bartender':
                bartender_profile = CustomUser.objects.filter(
                    id=employee.id, user_type='Bartender').first()
                if bartender_profile:
                    return CustomUserSerializer(bartender_profile).data
        return None

    def create(self, validated_data):
        ito_data = validated_data.pop('ITO', None)
        table_data = validated_data.pop('table', None)

        # Create the Order object
        order = Order.objects.create(**validated_data)

        # Create ItemToOrder objects
        if ito_data:
            for ito_item_data in ito_data:
                ItemToOrder.objects.create(order=order, **ito_item_data)

        # Create or update the associated table
        if table_data:
            table, _ = Table.objects.get_or_create(**table_data)
            order.table = table
            order.save()

        return order

    def get_total_sum(self, obj):
        total_sum = 0
        for ito in obj.ITO.all():
            total_price = ito.item.price_per_unit * ito.quantity
            total_sum += total_price
        obj.save()
        return total_sum

    def validate(self, data):
        if data.get('created_at') is None:
            data['created_at'] = timezone.now()  # Set current time as default
        if data.get('updated_at') is None:
            data['updated_at'] = timezone.now()  # Set current time as default
        return data


class OrderDetailedSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(default="Новый")
    total_sum = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    created_at = TimeField(required=False)
    updated_at = TimeField(required=False)
    completed_at = TimeField(allow_null=True, required=False)
    table = TableSerializer()
    employee_profile = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'table', 'order_status',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'order_type', 'total_sum', 'employee_profile', 'ITO']

    def update(self, instance, validated_data):
        # Update basic order information
        instance.order_status = validated_data.get(
            'order_status', instance.order_status)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.order_type = validated_data.get(
            'order_type', instance.order_type)
        instance.employee_profile = validated_data.get(
            'employee_profile', instance.employee)
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

    def get_employee_profile(self, instance):
        from users.models import CustomUser
        from users.serializers import CustomUserSerializer
        employee = instance.employee
        if employee:
            user_type = employee.user_type
            if user_type == 'Waiter':
                waiter_profile = CustomUser.objects.filter(
                    id=employee.id, user_type='Waiter').first()
                if waiter_profile:
                    return CustomUserSerializer(waiter_profile).data
            elif user_type == 'Bartender':
                bartender_profile = CustomUser.objects.filter(
                    id=employee.id, user_type='Bartender').first()
                if bartender_profile:
                    return CustomUserSerializer(bartender_profile).data
        return None


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
    ITO = ItemToOrderSerializer(many=True)
    created_at = TimeField(required=False, default=timezone.now)
    updated_at = TimeField(required=False, default=timezone.now)
    completed_at = TimeField(allow_null=True, required=False)
    customer_profile = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'order_status', "order_type",
                  'created_at', 'updated_at', 'completed_at', 'branch', 'total_sum', 'customer_profile', 'ITO', 'bonus_points_to_subtract']

    def get_customer_profile(self, instance):
        from users.models import CustomUser
        from users.serializers import CustomUserSerializer
        # Access the 'customer' attribute from the 'instance' object
        customer = instance.customer
        if customer:
            user_type = customer.user_type
            if user_type == "Customer":
                # Assuming 'customer_profile' is a related model field
                customer_profile = CustomUser.objects.filter(
                    id=customer.id, user_type="Customer").first()
                if customer_profile:
                    return CustomUserSerializer(customer_profile).data
        return None

    def create(self, validated_data):
        from users.models import CustomerProfile
        from users.serializers import CustomerProfileSerializer
        # Calculate total sum
        total_sum = self.get_total_sum(validated_data)
        print("total_sum", total_sum)

        # Calculate bonus points to subtract
        bonus_points_to_subtract = validated_data.get(
            'bonus_points_to_subtract', 0)
        print("bonus_points_to_subtract", bonus_points_to_subtract)

        # Retrieve the authenticated user
        authenticated_user = self.context['request'].user

        # Calculate the new bonus points
        new_bonus_points = authenticated_user.bonus_points - \
            bonus_points_to_subtract + \
            Decimal('0.1') * (total_sum - bonus_points_to_subtract)
        print("new_bonus_points", new_bonus_points)

        # Update the authenticated user's bonus points
        authenticated_user.bonus_points = new_bonus_points
        authenticated_user.save()

        # Continue with order creation
        ito_data = validated_data.pop('ITO', None)
        branch = validated_data.pop('branch', None)

        if not branch:
            raise serializers.ValidationError("Branch data is required.")

        branch_id = branch.id

        order = Order.objects.create(
            branch_id=branch_id, customer=authenticated_user, **validated_data)

        if ito_data:
            for ito_item_data in ito_data:
                ItemToOrder.objects.create(order=order, **ito_item_data)

        return order

    def get_total_sum(self, obj):
        self.is_valid()
        # Access 'ITO' from the validated data
        ito_data = self.validated_data.get('ITO', [])

        total_sum = 0
        for ito_item_data in ito_data:
            # Access the 'item' object directly
            item = ito_item_data['item']
            # Access the 'price_per_unit' attribute of the 'item'
            total_price = item.price_per_unit * ito_item_data['quantity']
            total_sum += total_price

        return total_sum

    def validate(self, data):
        if data.get('created_at') is None:
            data['created_at'] = timezone.now()  # Set current time as default
        if data.get('updated_at') is None:
            data['updated_at'] = timezone.now()  # Set current time as default
        return data

    def get_ITO(self, instance):
        # Get all ItemToOrder instances related to the Order instance
        ito_instances = instance.ITO.all()
        # Serialize the instances
        return ItemToOrderSerializer(ito_instances, many=True).data


##################


class OrderOnlineDetailedSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(default="Новый")
    total_sum = serializers.SerializerMethodField()
    ITO = ItemToOrderSerializer(many=True)
    created_at = TimeField(required=False, default=timezone.now)
    updated_at = TimeField(required=False, default=timezone.now)
    completed_at = TimeField(allow_null=True, required=False)
    customer_profile = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    bonus_points_to_subtract = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'order_status', 'order_type',
                  'created_at', 'updated_at', 'completed_at', 'branch', 'branch_name', 'total_sum', 'customer_profile', 'ITO', 'bonus_points_to_subtract']


    def update(self, instance, validated_data):
        # Update basic order information
        instance.order_status = validated_data.get(
            'order_status', instance.order_status)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.order_type = validated_data.get(
            'order_type', instance.order_type)
        instance.customer_profile = validated_data.get(
            'customer_profile', instance.customer)
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
            total_price = ito.item.price_per_unit * ito.quantity
            total_sum += total_price
        obj.save()
        return total_sum

    def get_customer_profile(self, instance):
        from users.models import CustomerProfile
        from users.serializers import CustomerProfileSerializer
        customer = instance.customer
        if customer and customer.user_type == "Customer":
            # Assuming 'customer_profile' is a related model field
            customer_profile = CustomerProfile.objects.filter(
                user=customer).first()
            if customer_profile:
                return CustomerProfileSerializer(customer_profile).data
        return None
    
    def get_branch_name(self, instance):
        return instance.branch.branch_name
