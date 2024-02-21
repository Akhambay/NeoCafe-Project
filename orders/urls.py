# urls.py
from django.urls import path
from .views import OrderCreateView, OrderListCreateView, OrderDetailView, CustomerOrderHistoryView

urlpatterns = [
    path('orders/add/', OrderCreateView.as_view(), name='order-create'),
    path('orders/all/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/history/', CustomerOrderHistoryView.as_view(),
         name='customer-order-history'),
]
