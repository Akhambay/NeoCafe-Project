# views.py

# from django.shortcuts import render
# from .models import Notification
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# def notifications_page(request):
#     #notifications = Notification.objects.filter(is_read=False, order__order_status='Готов')
#     return render(request, 'notifications.html')

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
        serialized_data = []
        for notification in notifications:
            order_message = self.construct_order_message(notification.order)
            notification_data = {
                'id': notification.id,
                'order_message': order_message,
                'is_read': notification.is_read,
                'created_at': notification.created_at
            }
            serialized_data.append(notification_data)
        return Response(serialized_data)

    def construct_order_message(self, order):
        items = [f"{ito.item.name} x {ito.quantity}" for ito in order.ito_set.all()]
        order_message = f"Order #{order.order_number} is ready. {order.completed_at.strftime('%H:%M')}, {' '.join(items)}"
        return order_message
