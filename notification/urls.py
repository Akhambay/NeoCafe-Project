from django.urls import path
from .views import NotificationListView, notifications_page

urlpatterns = [
    path('html_test/', notifications_page, name='notifications'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
]