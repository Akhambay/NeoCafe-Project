from rest_framework import serializers
from .models import CustomUser, Branch, Customer, Schedule, EmployeeSchedule
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


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
                            'confirmation_code', 'first_name', 'user_type', 'branch', 'schedule']
        model = CustomUser


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
                  'user_type', 'is_staff', 'branch', 'schedule']
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
        fields = ['id', 'username', 'password', 'first_name', 'email',
                  'user_type', 'is_staff', 'branch', 'employee_schedules']

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


"""
class EmployeeSerializer(serializers.ModelSerializer):
    schedule = EmployeeScheduleSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'first_name', 'email',
                  'user_type', 'is_staff', 'branch', 'schedule']

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedule', [])
        employee = CustomUser.objects.create(**validated_data)

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
"""


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'confirmation_code',]


class CustomerEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
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
        model = Customer
        fields = ['id', 'email', 'confirmation_code']
        read_only_fields = ['user_type',]


class CustomerLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'confirmation_code']


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
