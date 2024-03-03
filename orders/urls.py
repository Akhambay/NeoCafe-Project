# urls.py
from django.urls import path
from .views import (OrderView, OrderOnlineView, OrderListView, OrderOnlineListView, OrderDetailView,
                    CustomerOrderHistoryView, ModifyOrderView)

urlpatterns = [
    path('orders/add/', OrderView.as_view(), name='order-create'),
    path('orders-online/add/', OrderOnlineView.as_view(),
         name='order-online-create'),

    path('orders/all/', OrderListView.as_view(), name='order-list'),
    path('orders-online/all/', OrderOnlineListView.as_view(),
         name='order-online-list'),

    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/history/', CustomerOrderHistoryView.as_view(),
         name='customer-order-history'),
    path('orders/edit/', ModifyOrderView.as_view(), name='order-create'),
]
