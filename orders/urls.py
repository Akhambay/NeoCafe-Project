# urls.py
from django.urls import path
from .views import OrderCreateView, OrderListCreateView, OrderDetailView, CustomerOrderHistoryView
from .views import InVenueOrderView, TakeawayOrderView
urlpatterns = [
    path('orders/add/', OrderCreateView.as_view(), name='order-create'),
    path('orders/all/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/history/', CustomerOrderHistoryView.as_view(),
         name='customer-order-history'),
    path('invenue-orders/', InVenueOrderView.as_view(), name='invenue-orders'),
    path('takeaway-orders/', TakeawayOrderView.as_view(), name='takeaway-orders'),
]
