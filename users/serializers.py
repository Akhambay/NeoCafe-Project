from rest_framework import serializers
from .models import CustomUser, Branch, Customer


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


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'image', 'branch_name',
                  'address', 'phone_number', 'link_2gis', 'table_quantity', 'schedule', ]
        read_only_fields = ['description',]
        model = Branch


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'confirmation_code',]
