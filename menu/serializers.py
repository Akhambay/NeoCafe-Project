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
        # Update the Menu_Item instance fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.item_image = validated_data.get(
            'item_image', instance.item_image)
        instance.price_per_unit = validated_data.get(
            'price_per_unit', instance.price_per_unit)
        instance.branch = validated_data.get('branch', instance.branch)

        # Fetch or create Category instance based on its name
        category_data = validated_data.get('category')
        if category_data and 'name' in category_data:
            category_name = category_data['name']
            category_instance, _ = Category.objects.get_or_create(
                name=category_name)
            instance.category = category_instance

        instance.save()

        # Update or create ingredients
        ingredients_data = validated_data.get('ingredients', [])
        existing_ingredient_ids = []

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            if ingredient_id:
                # Update existing ingredient
                ingredient = Ingredient.objects.filter(
                    pk=ingredient_id, menu_item=instance).first()
                if ingredient:
                    ingredient.name = ingredient_data.get(
                        'name', ingredient.name)
                    ingredient.quantity = ingredient_data.get(
                        'quantity', ingredient.quantity)
                    ingredient.measurement_unit = ingredient_data.get(
                        'measurement_unit', ingredient.measurement_unit)
                    ingredient.save()
                    existing_ingredient_ids.append(ingredient_id)
            else:
                # Create new ingredient
                new_ingredient = Ingredient.objects.create(
                    menu_item=instance, **ingredient_data)
                existing_ingredient_ids.append(new_ingredient.id)

        # Delete ingredients that were not included in the update
        instance.ingredients.exclude(pk__in=existing_ingredient_ids).delete()

        return instance


class MenuItemSerializer(serializers.ModelSerializer):
    # Ensure read-only for ingredients
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Menu_Item
        fields = ['id', 'name', 'description', 'item_image',
                  'price_per_unit', 'branch', 'category', 'ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        menu_item = Menu_Item.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            # Add menu_item field to ingredient data
            ingredient_data['menu_item'] = menu_item
            Ingredient.objects.create(**ingredient_data)

        return menu_item


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

# class ExtraItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ExtraItem
#         fields = ['id', 'type_extra_product', 'name',  'quantity', 'measurement_unit',]