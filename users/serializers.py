from rest_framework import serializers
from .models import CustomUser, Branch, Customer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def get_credentials(self, data):
        username = data.get(self.username_field)
        password = data.get('password')

        if username and password:
            return {
                self.username_field: username,
                'password': password
            }
        return None

    def validate(self, attrs):
        credentials = self.get_credentials(attrs)

        if credentials is not None:
            user = authenticate(**credentials)

            if user and user.is_active:  # Check if the user is active
                refresh = self.get_token(user)

                return {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }

        raise serializers.ValidationError(
            'Unable to log in with provided credentials.')


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'username', 'password',]
        read_only_fields = ['last_name', 'email', 'bonus_points',
                            'confirmation_code', 'first_name', 'user_type', 'branch',]
        model = CustomUser
        # Schedule


class EmployeeAddSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'username', 'password', 'first_name',
                  'user_type', 'branch',]
        # read_only_fields = ['last_name', 'email', 'confirmation_code', ]
        model = CustomUser

    def create(self, validated_data):
        # Set a default email value if not provided during creation
        validated_data.setdefault('email', None)
        return super().create(validated_data)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password',
                  'user_type', 'branch', ]
        read_only_fields = ['confirmation_code', ]
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


class CustomerEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'confirmation_code']


class CustomerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'confirmation_code']
