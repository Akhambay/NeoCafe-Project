# views.py

from django.shortcuts import render
from .models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

def notifications_page(request):
    #notifications = Notification.objects.filter(is_read=False, order__order_status='Готов')
    return render(request, 'notifications.html')

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(APIView):
    def get(self, request):
        # Retrieve notifications for the authenticated user
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
