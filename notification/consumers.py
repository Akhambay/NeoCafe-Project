from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Notification
from asgiref.sync import sync_to_async

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
        notifications = await sync_to_async(list, thread_sensitive=True)(
            Notification.objects.filter(is_read=False)
        )
        notifications_list = []
        for notification in notifications:
            notifications_list.append(
                {
                    "order": notification.order,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.strftime("%d.%m.%Y"),
                }
            )
        await self.send(text_data=json.dumps({"notifications": notifications_list}))

    async def get_notification_handler(self, event):
        await self.get_notification()