from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .consumers import CustomerNotificationConsumer, WaiterNotificationConsumer, AdminNotificationConsumer, BartenderNotificationConsumer

websocket_urlpatterns = [
    path('ws/customer/<int:user_id>/', CustomerNotificationConsumer.as_asgi()),
    path('ws/waiter/<int:user_id>/', WaiterNotificationConsumer.as_asgi()),
    path('ws/admin/<int:user_id>/', AdminNotificationConsumer.as_asgi()),
    path('ws/bartender/<int:user_id>/', BartenderNotificationConsumer.as_asgi()),
]

# application = ProtocolTypeRouter({
#     'websocket': URLRouter(websocket_urlpatterns),
# })
