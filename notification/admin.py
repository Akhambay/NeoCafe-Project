from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'timestamp', 'status', 'recipient', 'table', 'read')
    fields = ('title', 'description', 'timestamp', 'status', 'recipient', 'table', 'read')
    readonly_fields = ('timestamp',)
