# consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from .models import Notification


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass  # Disconnection handling if needed

    def receive(self, text_data):
        # Handle incoming WebSocket messages
        pass

    def send_notification(self, event):
        # Send notification to the client
        notification = event['notification']
        self.send(text_data=json.dumps(notification))
