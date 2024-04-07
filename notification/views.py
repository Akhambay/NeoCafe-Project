# views.py

from django.shortcuts import render
from .models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

def notifications_page(request):
    #notifications = Notification.objects.filter(is_read=False, order__order_status='Готов')
    return render(request, 'notifications.html')
