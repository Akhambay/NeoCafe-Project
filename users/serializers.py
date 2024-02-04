from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'username', 'password',]
        read_only_fields = ['last_name', 'email',
                            'avatar', 'bonus_points', 'confirmation_code', 'first_name', 'user_type', 'DOB', 'phone_number', 'branch',]
        model = CustomUser
        # Schedule


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'username', 'password', 'first_name',
                  'user_type', 'DOB', 'phone_number', 'branch',]
        read_only_fields = ['last_name', 'email',
                            'avatar', 'bonus_points', 'confirmation_code', ]
        model = CustomUser
