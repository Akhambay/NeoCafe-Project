# notification/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def receive(self, text_data):
        pass  # We don't need to handle receiving messages from clients

    async def send_notification(self, event):
        notification = event["notification"]
        await self.send(text_data=json.dumps(notification))
