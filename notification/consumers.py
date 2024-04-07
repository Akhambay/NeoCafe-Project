from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Notification
from orders.serializers import OrderSerializer  # Assuming you have a serializer for Order

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONNECT")
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()
        print("GET NOTIFICATION")
        await self.get_notification()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def receive(self, text_data):
        pass  # We don't need to handle receiving messages from clients

    async def get_notification(self, event=None):
        notifications = await self.get_notifications_async()
        await self.send(text_data=json.dumps({"notifications": notifications}))

    @database_sync_to_async
    def get_notifications_async(self):
        notifications = Notification.objects.filter(is_read=False)
        notifications_list = []
        for notification in notifications:
            notifications_list.append(
                {
                    "order": self.serialize_order(notification.order),
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.strftime("%d.%m.%Y"),
                }
            )
        return notifications_list

    def serialize_order(self, order):
        serializer = OrderSerializer(order)  # Use your Order serializer
        return serializer.data

    async def get_notification_handler(self, event):
        await self.get_notification()
