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
        # Assuming notifications are related to orders, filter notifications based on orders associated with the authenticated user
        user_orders = request.user.orders.all()
        notifications = Notification.objects.filter(order__in=user_orders)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
