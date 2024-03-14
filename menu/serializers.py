from .models import Stock
from rest_framework import serializers
from .models import Menu_Item, Category, Stock, Ingredient


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'image']
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


class CategoryNoImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
        model = Category


class MenuItemListSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    category = CategoryNoImageSerializer()

    class Meta:
        model = Menu_Item
        fields = ['id', 'name', 'description', 'item_image',
                  'price_per_unit', 'branch', 'category', 'ingredients']

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        instance = super().update(instance, validated_data)

        # Track existing ingredient IDs to avoid duplicates
        existing_ingredient_ids = set()

        # Update existing ingredients or create new ones
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id', None)
            if ingredient_id:
                # If ingredient ID exists, update existing ingredient
                ingredient = Ingredient.objects.filter(
                    pk=ingredient_id, menu_item=instance).first()
                if ingredient:
                    ingredient.name = ingredient_data.get(
                        'name', ingredient.name)
                    ingredient.save()
                    existing_ingredient_ids.add(ingredient_id)
            else:
                # If ingredient ID does not exist, create new ingredient
                new_ingredient = Ingredient.objects.create(
                    menu_item=instance, **ingredient_data)
                existing_ingredient_ids.add(new_ingredient.id)

        # Delete ingredients that were not included in the update
        instance.ingredients.exclude(pk__in=existing_ingredient_ids).delete()

        return instance


class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

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
        instance = super().update(instance, validated_data)

        # Track existing ingredient IDs to avoid duplicates
        existing_ingredient_ids = set()

        # Update existing ingredients or create new ones
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id', None)
            if ingredient_id:
                # If ingredient ID exists, update existing ingredient
                ingredient = Ingredient.objects.filter(
                    pk=ingredient_id, menu_item=instance).first()
                if ingredient:
                    ingredient.name = ingredient_data.get(
                        'name', ingredient.name)
                    ingredient.save()
                    existing_ingredient_ids.add(ingredient_id)
            else:
                # If ingredient ID does not exist, create new ingredient
                new_ingredient = Ingredient.objects.create(
                    menu_item=instance, **ingredient_data)
                existing_ingredient_ids.add(new_ingredient.id)

        # Delete ingredients that were not included in the update
        instance.ingredients.exclude(pk__in=existing_ingredient_ids).delete()

        return instance


class StockSerializer(serializers.ModelSerializer):
    branch_id = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'stock_item', 'current_quantity', 'measurement_unit',
                  'minimum_limit', 'type', 'restock_date', 'branch_id', 'branch_name',]
        model = Stock

    def get_branch_id(self, obj):
        return obj.branch.id if obj.branch else None

    def get_branch_name(self, obj):
        return obj.branch.branch_name if obj.branch else None

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


class StockAddSerializer(serializers.ModelSerializer):
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
