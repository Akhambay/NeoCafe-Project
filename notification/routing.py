# notification/routing.py

from django.urls import re_path
from .consumers import WaiterNotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/waiter/(?P<user_id>\d+)/$', WaiterNotificationConsumer.as_asgi()),
]
