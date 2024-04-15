from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from .consumers import CustomerNotificationConsumer, WaiterNotificationConsumer, AdminNotificationConsumer, BartenderNotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/customer/(?P<user_id>\d+)/$', CustomerNotificationConsumer.as_asgi()),
    re_path(r'ws/waiter/(?P<user_id>\d+)/$', WaiterNotificationConsumer.as_asgi()),
    re_path(r'ws/admin/(?P<user_id>\d+)/$', AdminNotificationConsumer.as_asgi()),
    re_path(r'ws/bartender/(?P<user_id>\d+)/$', BartenderNotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),
})
