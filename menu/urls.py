from django.urls import path, include
from .views import (MenuItemCreateView, MenuItemList, MenuItemDetail,
                    CategoryCreateView, CategoryList, CategoryDetail,
                    IngredientCreateView, IngredientList, IngredientDetail,
                    IngredientNotEnoughList, IngredientEnoughList,)

urlpatterns = [
    path('menu/item/add/', MenuItemCreateView.as_view(), name='menu_item'),
    path('menu/item/all/', MenuItemList.as_view(), name='menu_item'),
    path('menu/item/<int:pk>/', MenuItemDetail.as_view(), name='menu_item'),

    path('menu/category/add/', CategoryCreateView.as_view(), name='menu_category'),
    path('menu/category/all/', CategoryList.as_view(), name='menu_category'),
    path('menu/category/<int:pk>/', CategoryDetail.as_view(), name='menu_category'),

    path('stock/ingredients/add/',
         IngredientCreateView.as_view(), name='ingredient_item'),
    path('stock/ingredients/all/', IngredientList.as_view(), name='ingredient_item'),
    path('stock/ingredients/<int:pk>/',
         IngredientDetail.as_view(), name='ingredient_item'),

    path('stock/ingredients/not_much/',
         IngredientNotEnoughList.as_view(), name='ingredient_item'),
    path('stock/ingredients/enough/',
         IngredientEnoughList.as_view(), name='ingredient_item'),
]
