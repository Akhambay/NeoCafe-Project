from rest_framework import serializers
from .models import Notification


class UserNotificationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    #title = serializers.CharField(max_length=255)
    #description = serializers.CharField(max_length=255)

    class Meta:
        model = Notification
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['title'] = ret['title'].encode('utf-8').decode('unicode_escape')
        ret['description'] = ret['description'].encode('utf-8').decode('unicode_escape')
        return ret
