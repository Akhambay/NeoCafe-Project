# urls.py
from django.urls import path
from .views import OrderView, OrderListCreateView, OrderDetailView, CustomerOrderHistoryView, ModifyOrderView

urlpatterns = [
    path('orders/add/', OrderView.as_view(), name='order-create'),
    path('orders/all/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/history/', CustomerOrderHistoryView.as_view(),
         name='customer-order-history'),
    path('orders/edit/', ModifyOrderView.as_view(), name='order-create'),
]
