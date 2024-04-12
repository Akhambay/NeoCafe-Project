from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Notification
from orders.serializers import OrderSerializer

from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from django.utils import timezone

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         print("CONNECT")
#         await self.channel_layer.group_add("notifications", self.channel_name)
#         await self.accept()
#         print("GET NOTIFICATION")
#         await self.get_notification()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("notifications", self.channel_name)

#     async def receive(self, text_data):
#         pass  # We don't need to handle receiving messages from clients

#     async def get_notification(self, event=None):
#         notifications = await self.get_notifications_async()
#         await self.send(text_data=json.dumps({"notifications": notifications}))

#     @database_sync_to_async
#     def get_notifications_async(self):
#         notifications = Notification.objects.filter(is_read=False)
#         notifications_list = []
#         for notification in notifications:
#             notifications_list.append(
#                 {
#                     "order": self.serialize_order(notification.order),
#                     "is_read": notification.is_read,
#                     "created_at": notification.created_at.strftime("%d.%m.%Y"),
#                 }
#             )
#         return notifications_list

#     def serialize_order(self, order):
#         serializer = OrderSerializer(order)  # Use your Order serializer
#         return serializer.data

#     async def get_notification_handler(self, event):
#         await self.get_notification()

class WaiterNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer for sending notifications to waiter.
    """

    async def connect(self):
        self.employee_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.employee = await self.get_user(self.employee_id)
        print(self.employee)
        if self.employee.position == 'Waiter':
            self.user_group_name = f"waiter-{self.employee.id}"

            # Connect to user-specific group
            await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        await self.get_notifications()
        pass

    @database_sync_to_async
    def get_user(self, employee_id):
        return get_user_model().objects.get(id=employee_id)


    async def disconnect(self, close_code):
        # Disconnect from group
        await self.channel_layer.group_discard(
            self.user_group_name, self.channel_name
        )
        pass

    async def get_notifications(self, event=None):
        notifications = await sync_to_async(list, thread_sensitive=True)(
            Notification.objects.filter(recipient=self.employee, read=False).order_by('-timestamp')
        )
        notifications_list = []
        for notification in notifications:
            notifications_list.append(
                {
                    "id": notification.id,
                    "title": notification.title,
                    "description": notification.description,
                    "timestamp": notification.timestamp.strftime("%H:%M"),
                }
            )
            notification.read = True
            await sync_to_async(notification.save, thread_sensitive=True)()
        await self.send(text_data=json.dumps({"notifications": notifications_list}))
        pass

    async def get_notifications_handler(self, event):
        await self.get_notifications()

    async def receive(self, text_data):
        ...
        # text_data_json = json.loads(text_data)
        pass

    async def receive_get_notifications(self, event):
        await self.get_notifications()