from django.urls import path, include
from .views import (MenuItemCreateView, MenuItemList, MenuItemDetail,
                    CategoryCreateView, CategoryList, CategoryDetail)

urlpatterns = [
    path('menu/item/', MenuItemCreateView.as_view(), name='menu_item'),
    path('menu/item/all/', MenuItemList.as_view(), name='menu_item'),
    path('menu/item/<int:pk>/', MenuItemDetail.as_view(), name='menu_item'),

    path('menu/category/', CategoryCreateView.as_view(), name='menu_item'),
    path('menu/category/all/', CategoryList.as_view(), name='menu_item'),
    path('menu/category/<int:pk>/', CategoryDetail.as_view(), name='menu_item'),
]
