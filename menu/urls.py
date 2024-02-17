from django.urls import path, include
from .views import (MenuItemCreateView, MenuItemList, MenuItemDetail,
                    CategoryCreateView, CategoryList, CategoryDetail,
                    StockItemCreateView, StockItemsList, StockItemDetail,
                    StockItemsNotEnoughList, StockItemsEnoughList, StockItemsRawEnoughList
                    )

urlpatterns = [
    path('menu/item/add/', MenuItemCreateView.as_view(), name='menu_item'),
    path('menu/item/all/', MenuItemList.as_view(), name='menu_item'),
    path('menu/item/<int:pk>/', MenuItemDetail.as_view(), name='menu_item'),

    path('menu/category/add/', CategoryCreateView.as_view(), name='menu_category'),
    path('menu/category/all/', CategoryList.as_view(), name='menu_category'),
    path('menu/category/<int:pk>/', CategoryDetail.as_view(), name='menu_category'),

    path('stock/items/add/',
         StockItemCreateView.as_view(), name='stock_item'),
    path('stock/items/all/', StockItemsList.as_view(), name='stock_item'),
    path('stock/items/<int:pk>/',
         StockItemDetail.as_view(), name='stock_item'),

    path('stock/items/not_much/',
         StockItemsNotEnoughList.as_view(), name='available_item'),
    path('stock/items/enough/',
         StockItemsEnoughList.as_view(), name='available_item'),
    path('stock/items/raw_enough/',
         StockItemsRawEnoughList.as_view(), name='available_item'),
]
