from rest_framework import serializers
from .models import (CustomUser, Branch, Schedule,
                     EmployeeSchedule, EmployeeProfile, CustomerProfile,
                     WaiterProfile, BartenderProfile)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'username', 'password',]
        read_only_fields = ['last_name', 'email', 'bonus_points',
                            'confirmation_code', 'first_name', 'user_type', 'branch', 'schedule']
        model = CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken.for_user(self.user)

        # Serialize the user object
        user_serializer = CustomUserSerializer(self.user)
        serialized_user = user_serializer.data

        # Add the serialized user to the validated data
        data['user'] = serialized_user

        # Add the refresh token to the validated data
        data['refresh'] = str(refresh)

        return data


class ScheduleSerializer(serializers.Serializer):
    day = serializers.ChoiceField(choices=Schedule.DAYS_CHOICES)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate(self, data):
        return data


class EmployeeScheduleSerializer(serializers.Serializer):
    day = serializers.ChoiceField(choices=EmployeeSchedule.DAYS_CHOICES)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    def validate(self, data):
        return data


class EmployeeAddSerializer(serializers.ModelSerializer):
    schedule = EmployeeScheduleSerializer(many=True)

    class Meta:
        fields = ['id', 'username', 'password', 'first_name', 'email',
                  'user_type', 'branch', 'schedule']
        model = CustomUser

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedule', [])

        # Create the employee
        employee = CustomUser.objects.create(**validated_data)

        # Create schedules associated with the employee
        for schedule_data in schedules_data:
            EmployeeSchedule.objects.create(employee=employee, **schedule_data)

        return employee

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedule', [])
        instance = super().update(instance, validated_data)

        # Update or create Schedule instances based on the provided data
        existing_schedules = instance.schedule.all()
        for schedule_data in schedules_data:
            day = schedule_data['day']
            schedule_instance = existing_schedules.filter(day=day).first()

            if schedule_instance:
                # Update existing schedule
                schedule_instance.start_time = schedule_data['start_time']
                schedule_instance.end_time = schedule_data['end_time']
                schedule_instance.save()
            else:
                # Create new schedule
                EmployeeSchedule.objects.create(
                    employee=instance, **schedule_data)

        return instance


class BranchSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)

    class Meta:
        model = Branch
        fields = '__all__'

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        branch = Branch.objects.create(**validated_data)

        for schedule_data in schedules_data:
            Schedule.objects.create(branch=branch, **schedule_data)

        return branch

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        instance = super().update(instance, validated_data)

        # Update or create Schedule instances based on the provided data
        existing_schedules = instance.schedules.all()
        for schedule_data in schedules_data:
            day = schedule_data['day']
            schedule_instance = existing_schedules.filter(day=day).first()

            if schedule_instance:
                # Update existing schedule
                schedule_instance.start_time = schedule_data['start_time']
                schedule_instance.end_time = schedule_data['end_time']
                schedule_instance.save()
            else:
                # Create new schedule
                Schedule.objects.create(branch=instance, **schedule_data)

        return instance


class EmployeeSerializer(serializers.ModelSerializer):
    employee_schedules = EmployeeScheduleSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email',
                  'user_type', 'branch', 'employee_schedules']

    def create(self, validated_data):
        schedules_data = validated_data.pop('employee_schedules', [])
        employee = CustomUser.objects.create(**validated_data)

        for schedule_data in schedules_data:
            EmployeeSchedule.objects.create(employee=employee, **schedule_data)

        return employee

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('employee_schedules', [])
        instance = super().update(instance, validated_data)

        # Update or create Schedule instances based on the provided data
        existing_schedules = instance.employee_schedules.all()
        existing_schedule_ids = [
            schedule.id for schedule in existing_schedules]

        for schedule_data in schedules_data:
            schedule_id = schedule_data.get('id')

            if schedule_id and schedule_id in existing_schedule_ids:
                # Update existing schedule
                schedule_instance = existing_schedules.get(id=schedule_id)
                schedule_instance.day = schedule_data['day']
                schedule_instance.start_time = schedule_data['start_time']
                schedule_instance.end_time = schedule_data['end_time']
                schedule_instance.save()
            else:
                # Create new schedule if it doesn't exist
                EmployeeSchedule.objects.create(
                    employee=instance, **schedule_data)

        # Delete any schedules that were not included in the update data
        schedule_ids_to_delete = [schedule.id for schedule in existing_schedules if schedule.id not in [
            s.get('id') for s in schedules_data]]
        EmployeeSchedule.objects.filter(id__in=schedule_ids_to_delete).delete()

        return instance


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'confirmation_code',]


class CustomerEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', ]


User = get_user_model()


class CustomerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'confirmation_code']

    def create(self, validated_data):
        """
        Retrieve an existing user based on email and confirmation code.
        """
        email = validated_data['email']
        confirmation_code = validated_data['confirmation_code']

        # Check if the user already exists
        user = User.objects.filter(
            email=email, confirmation_code=confirmation_code).first()

        if user is None:
            # If no user is found, you may raise an exception or handle it as needed
            raise serializers.ValidationError(
                "User not found with the provided email and confirmation code")

        return user


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'confirmation_code']
        read_only_fields = ['user_type', 'bonus_points', 'first_name',]


class CustomerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'confirmation_code', 'first_name']
        read_only_fields = ['first_name',]


class CustomerAuthenticationCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email', None)

        # Check if the email is in the database
        user_exists = get_user_model().objects.filter(email=email).exists()

        if not user_exists:
            # You can add additional validation if needed
            # For example, check if the email format is valid

            return data
        else:
            # If the email exists, proceed with sending a new confirmation code
            return data

# Bartender


class BartenderAuthenticationCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email', None)

        # Check if the email is in the database
        user_exists = get_user_model().objects.filter(email=email).exists()

        if not user_exists:
            # You can add additional validation if needed
            # For example, check if the email format is valid

            return data
        else:
            # If the email exists, proceed with sending a new confirmation code
            return data


class BartenderLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'confirmation_code']

    def create(self, validated_data):
        """
        Retrieve an existing user based on email and confirmation code.
        """
        email = validated_data['email']
        confirmation_code = validated_data['confirmation_code']

        # Check if the user already exists
        user = User.objects.filter(
            email=email, confirmation_code=confirmation_code).first()

        if user is None:
            # If no user is found, you may raise an exception or handle it as needed
            raise serializers.ValidationError(
                "User not found with the provided email and confirmation code")

        return user

# WAITER


class WaiterAuthenticationCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email', None)

        # Check if the email is in the database
        user_exists = get_user_model().objects.filter(email=email).exists()

        if not user_exists:
            # You can add additional validation if needed
            # For example, check if the email format is valid

            return data
        else:
            # If the email exists, proceed with sending a new confirmation code
            return data


class WaiterLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'confirmation_code']

    def create(self, validated_data):
        """
        Retrieve an existing user based on email and confirmation code.
        """
        email = validated_data['email']
        confirmation_code = validated_data['confirmation_code']

        # Check if the user already exists
        user = User.objects.filter(
            email=email, confirmation_code=confirmation_code).first()

        if user is None:
            # If no user is found, you may raise an exception or handle it as needed
            raise serializers.ValidationError(
                "User not found with the provided email and confirmation code")

        return user


class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        read_only_fields = '__all__'


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['id', 'first_name', 'bonus', 'email', 'orders',]
        read_only_fields = ['email', 'bonus', 'orders']


class WaiterProfileSerializer(serializers.ModelSerializer):
    # Include the EmployeeSerializer to represent the related employee
    employee = EmployeeSerializer()
    schedule = EmployeeScheduleSerializer(many=True)

    class Meta:
        model = WaiterProfile
        fields = '__all__'
        read_only_fields = ['employee', 'first_name',
                            'last_name', 'email', 'schedule']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Remove unwanted fields
        for field in ['schedule', 'first_name', 'last_name', 'email']:
            data.pop(field, None)

        return data


class BartenderProfileSerializer(serializers.ModelSerializer):
    # Include the EmployeeSerializer to represent the related employee
    employee = EmployeeSerializer()
    schedule = EmployeeScheduleSerializer(many=True)

    class Meta:
        model = BartenderProfile
        fields = '__all__'
        read_only_fields = ['employee', 'first_name',
                            'last_name', 'email', 'schedule']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Remove unwanted fields
        for field in ['schedule', 'first_name', 'last_name', 'email']:
            data.pop(field, None)

        return data
