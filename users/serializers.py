from datetime import datetime
from rest_framework import serializers
from .models import (CustomUser, Branch, Schedule,
                     EmployeeSchedule, CustomerProfile, Profile,
                     WaiterProfile, BartenderProfile)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model, login
from rest_framework_simplejwt.tokens import RefreshToken
from orders.serializers import OrderSerializer, OrderOnlineSerializer
from orders.models import Order


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
    day = serializers.ChoiceField(choices=EmployeeSchedule.DAYS_CHOICES)
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    def validate(self, data):
        return data


class EmployeeScheduleSerializer(serializers.Serializer):
    day = serializers.ChoiceField(choices=EmployeeSchedule.DAYS_CHOICES)
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = EmployeeSchedule
        fields = ['id', 'day', 'start_time', 'end_time']

    def validate(self, data):
        return data


class EmployeeAddSerializer(serializers.ModelSerializer):
    employee_schedules = EmployeeScheduleSerializer(many=True)

    class Meta:
        fields = ['id', 'username', 'password', 'first_name', 'email',
                  'user_type', 'branch', 'employee_schedules']
        model = CustomUser

    def create(self, validated_data):
        schedules_data = validated_data.pop('employee_schedules', [])

        # Create the employee
        employee = CustomUser.objects.create(**validated_data)

        # Create schedules associated with the employee
        for schedule_data in schedules_data:
            EmployeeSchedule.objects.create(employee=employee, **schedule_data)

        return employee

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('employee_schedules', [])
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
        fields = ["id", "branch_name", "address", "phone_number",
                  "link_2gis", "table_quantity", "image", "description", "schedules"]

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


class BranchEditSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True)

    class Meta:
        model = Branch
        fields = ["id", "branch_name", "address", "phone_number",
                  "link_2gis", "table_quantity", "image", "description", "schedules"]

    def update(self, instance, validated_data):
        schedules_data = validated_data.pop('schedules', [])
        instance = super().update(instance, validated_data)

        # Update or create Schedule instances based on the provided data
        existing_schedules = instance.schedules.all()
        existing_days = [schedule.day for schedule in existing_schedules]

        # Remove schedules for days not present in the input data
        for existing_schedule in existing_schedules:
            if existing_schedule.day not in [schedule_data['day'] for schedule_data in schedules_data]:
                existing_schedule.delete()

        # Update or create schedules for input data
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
    # branch = BranchSerializer()
    branch_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email',
                  'user_type', 'branch', 'branch_name', 'employee_schedules', ]

    def get_branch_name(self, obj):
        return obj.branch.branch_name if obj.branch else None

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
        fields = ['id', 'username', 'password', 'first_name', 'email',
                  'user_type', 'bonus_points', 'orders', ]

    def create(self, validated_data):
        return CustomUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CustomerEmailConfirmSerializer(serializers.ModelSerializer):
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
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Check if the username is in the database
        user = get_user_model().objects.filter(username=username).first()

        if user:
            data['user'] = user
        else:
            raise serializers.ValidationError(
                "Waiter with this username is not registered.")

        return data
# ===========================================================================
# WAITER AUTHENTICATION
# ===========================================================================


class WaiterLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        confirmation_code = data.get('confirmation_code')

        # Retrieve user data from the session
        pending_user_data = self.context['request'].session.get(
            'pending_confirmation_user')

        user_id = pending_user_data.get('user_id')

        user = get_user_model().objects.filter(
            id=user_id, email=email, confirmation_code=confirmation_code).first()

        if user is not None:
            # Add 'user' to validated_data before returning
            data['user'] = user

            # Login the user
            login(self.context['request'], user)

            return data
        else:
            raise serializers.ValidationError("Invalid confirmation code.")


class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        read_only_fields = '__all__'


class WaiterProfileSerializer(serializers.ModelSerializer):
    # Include the EmployeeSerializer to represent the related employee
    user = EmployeeSerializer()
    schedule = EmployeeScheduleSerializer(many=True)

    class Meta:
        model = WaiterProfile
        fields = '__all__'
        read_only_fields = ['id', 'user', 'schedule']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Remove unwanted fields
        for field in ['schedule', 'first_name', 'schedule', 'user_type', 'branch', 'last_name', 'email']:
            data.pop(field, None)

        return data


class CustomerProfileSerializer(serializers.ModelSerializer):
    # Define serializer fields
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    bonus_points = serializers.IntegerField(source='user.bonus_points', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user_id', 'first_name', 'email', 'bonus_points']

    def create(self, validated_data):
        # Extract user-related data from validated_data
        user_data = validated_data.pop('user', None)

        # Check if user_data exists and the user is a customer
        if user_data and user_data.get('user_type') == 'Customer':
            # Create or retrieve the CustomUser instance
            user, created = CustomUser.objects.update_or_create(
                email=user_data.get('email'),
                defaults={'first_name': user_data.get('first_name')}
            )

            # Create CustomerProfile instance
            customer_profile = CustomerProfile.objects.create(user=user, **validated_data)
            return customer_profile

        # If the user is not a customer, raise an exception
        raise serializers.ValidationError("Go ahead")

    def update(self, instance, validated_data):
        # Update only if 'first_name' is provided in the validated data
        user_data = validated_data.pop('user', None)
        if user_data and 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
            instance.user.save()

        # Update CustomerProfile instance
        return super().update(instance, validated_data)


class BartenderProfileSerializer(serializers.ModelSerializer):
    # Include the EmployeeSerializer to represent the related employee
    user = EmployeeSerializer()
    schedule = EmployeeScheduleSerializer(many=True)

    class Meta:
        model = BartenderProfile
        fields = '__all__'
        read_only_fields = ['user', 'first_name',
                            'last_name', 'email', 'schedule']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Remove unwanted fields
        for field in ['schedule', 'first_name', 'last_name', 'email']:
            data.pop(field, None)

        return data
