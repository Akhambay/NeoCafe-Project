# views.py

from django.shortcuts import render
from .models import Notification
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

def notifications_page(request):
    notifications = Notification.objects.all()  # Fetch all notifications from the database
    return render(request, 'notifications.html', {'notifications': notifications})



class NotificationDeleteView(APIView):

    def delete(self, request, id):
        notification = Notification.objects.get(id=id)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationCreateView(APIView):

    def post(self, request):
        title = request.data.get('title')
        message = request.data.get('message')
        notification = Notification(title=title, message=message)
        notification.save()
        return Response(status=status.HTTP_201_CREATED)