from .models import Stock
from rest_framework import serializers
from .models import Menu_Item, Category, Stock, Ingredient


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name',]
        model = Category


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'quantity', 'measurement_unit']
        model = Ingredient

    def to_internal_value(self, data):
        # Convert user input to internal representation before validation
        data['quantity'], data['measurement_unit'] = self.convert_quantity(
            data.get('quantity'), data.get('measurement_unit'))

        return super().to_internal_value(data)

    def convert_quantity(self, quantity, measurement_unit):
        # Convert quantity to grams for kg and liters to milliliters
        if measurement_unit == 'кг':
            quantity *= 1000  # 1 kg = 1000 g
            measurement_unit = 'гр'
        elif measurement_unit == 'л':
            quantity *= 1000  # 1 liter = 1000 ml
            measurement_unit = 'мл'

        return quantity, measurement_unit


class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)
    category = CategorySerializer()

    class Meta:
        model = Menu_Item
        fields = ['id', 'name', 'description', 'item_image',
                  'price_per_unit', 'branch', 'category', 'ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        menu_item = Menu_Item.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(menu_item=menu_item, **ingredient_data)

        return menu_item

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])

        # Update Menu_Item fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.item_image = validated_data.get(
            'item_image', instance.item_image)
        instance.price_per_unit = validated_data.get(
            'price_per_unit', instance.price_per_unit)
        instance.category = validated_data.get('category', instance.category)
        instance.save()

        # Update or create Ingredient instances based on the provided data
        for ingredient_data in ingredients_data:
            name = ingredient_data['name']
            quantity = ingredient_data['quantity']
            measurement_unit = ingredient_data['measurement_unit']

            ingredient_instance, created = Ingredient.objects.get_or_create(
                menu_item=instance,
                name=name,
                defaults={'quantity': quantity,
                          'measurement_unit': measurement_unit}
            )

            if not created:
                # Update existing Ingredient
                ingredient_instance.quantity = quantity
                ingredient_instance.measurement_unit = measurement_unit
                ingredient_instance.save()

        return instance


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'stock_item', 'current_quantity', 'measurement_unit',
                  'minimum_limit', 'type', 'restock_date', 'branch']
        model = Stock

    def to_internal_value(self, data):
        # Convert user input to internal representation before validation
        data['current_quantity'], data['measurement_unit'], data['minimum_limit'] = self.convert_quantity(
            data.get('current_quantity'), data.get('measurement_unit'), data.get('minimum_limit'))

        return super().to_internal_value(data)

    def convert_quantity(self, quantity, measurement_unit, minimum_limit):
        # Convert quantity to grams for kg and liters to milliliters
        if measurement_unit == 'кг':
            quantity *= 1000  # 1 kg = 1000 g
            measurement_unit = 'гр'
            minimum_limit *= 1000
        elif measurement_unit == 'л':
            quantity *= 1000  # 1 liter = 1000 ml
            measurement_unit = 'мл'
            minimum_limit *= 1000

        return quantity, measurement_unit, minimum_limit

    def create(self, validated_data):
        # Convert user input to internal representation before creating the instance
        validated_data['current_quantity'], validated_data['measurement_unit'], validated_data['minimum_limit'] = self.convert_quantity(
            validated_data.get('current_quantity'), validated_data.get('measurement_unit'), validated_data.get('minimum_limit'))

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Convert user input to internal representation before updating the instance
        validated_data['current_quantity'], validated_data['measurement_unit'], validated_data['minimum_limit'] = self.convert_quantity(
            validated_data.get('current_quantity'), validated_data.get('measurement_unit'), validated_data.get('minimum_limit'))

        return super().update(instance, validated_data)
