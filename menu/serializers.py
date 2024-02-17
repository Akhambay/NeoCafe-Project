from rest_framework import serializers
from .models import Menu_Item, Category, Stock, Ingredient


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name',]
        model = Category


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'quantity', 'measurement_unit',]
        model = Ingredient


class MenuItemSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Menu_Item
        fields = '__all__'

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        menu_item = Menu_Item.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(menu_item=menu_item, **ingredient_data)

        return menu_item

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        instance = super().update(instance, validated_data)

        # Update or create Ingredient instances based on the provided data
        existing_ingredients = instance.ingredients.all()
        for ingredient_data in ingredients_data:
            name = ingredient_data['name']
            quantity = ingredient_data['quantity']
            measurement_unit = ingredient_data['measurement_unit']

            ingredient_instance, _ = existing_ingredients.get_or_create(
                name=name,
                defaults={'quantity': quantity,
                          'measurement_unit': measurement_unit}
            )

        return instance


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'stock_item', 'current_quantity', 'measurement_unit',
                  'minimum_limit', 'type', 'restock_date', 'branch']
        model = Stock
