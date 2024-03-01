from rest_framework.pagination import PageNumberPagination
from rest_framework.views import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import (
    CustomerEmailSerializer, CustomerRegistrationSerializer, CustomerLoginSerializer,
    CustomerAuthenticationCheckSerializer, EmployeeAddSerializer,
    BranchSerializer, EmployeeSerializer, ScheduleSerializer, EmployeeScheduleSerializer,
    BartenderAuthenticationCheckSerializer, BartenderLoginSerializer,
    WaiterAuthenticationCheckSerializer, WaiterLoginSerializer,
    CustomerProfileSerializer, EmployeeProfileSerializer,
    AdminLoginSerializer, CustomTokenObtainPairSerializer, CustomerProfile, Profile,
    WaiterProfileSerializer, BartenderProfileSerializer,
)
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from dj_rest_auth.serializers import JWTSerializer, TokenSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from .models import CustomUser, Branch, Schedule, EmployeeSchedule, WaiterProfile, BartenderProfile
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.registration.views import RegisterView
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from dj_rest_auth.models import TokenModel
from rest_framework_simplejwt.tokens import Token
from dj_rest_auth.utils import jwt_encode
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
# ===========================================================================
# TOKEN OBTAIN
# ===========================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ===========================================================================
# TOKEN REFRESH
# ===========================================================================


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.data.get('refresh', None)

        if not refresh:
            return Response({'detail': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data.get('access', None)

        if not access_token:
            return Response({'detail': 'Access token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'refresh': str(refresh), 'access': str(access_token)})


obtain_jwt_token = CustomTokenObtainPairView.as_view()
token_refresh = CustomTokenRefreshView.as_view()

# ===========================================================================
# ADMIN LOGIN TOKEN
# ===========================================================================


class AdminLoginTokenView(TokenObtainPairView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # If login is successful, modify the response to exclude access token
        if response.status_code == 200:
            # Remove the 'access' key from the response data
            response.data.pop('access', None)

        return response


# ===========================================================================
# EMPLOYEE
# ===========================================================================
def create_employee_profile(employee, user_type, schedules_data, profile_model, schedule_model):
    # Create or retrieve profile
    employee_profile, created = profile_model.objects.get_or_create(
        employee=employee)

    # Check if the profile was created or already existed
    if created:
        # Create Schedule instances and associate them with the profile
        for schedule_data in schedules_data:
            day = schedule_data['day']
            start_time = schedule_data['start_time']
            end_time = schedule_data['end_time']

            # Check if a similar schedule already exists
            existing_schedule = schedule_model.objects.filter(
                day=day, start_time=start_time, end_time=end_time, employee=employee).first()

            if not existing_schedule:
                # Create Schedule instance
                schedule_instance = schedule_model.objects.create(
                    day=day, start_time=start_time, end_time=end_time, employee=employee)

############


class EmployeeCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer

    def validate_password_length(self, password):
        if not (4 <= len(password) <= 10):
            return "Password must be between 4 and 10 characters."

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate password length
        password = serializer.validated_data.get('password')
        password_length_message = self.validate_password_length(password)

        if password_length_message:
            return Response({'error': password_length_message}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password using Django's built-in validators
        try:
            validate_password(password)
        except ValidationError as e:
            return "Password must be between 4 and 10 characters."

        self.perform_create(serializer)

        refresh = RefreshToken.for_user(serializer.instance)
        token_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        headers = self.get_success_headers(serializer.data)
        return Response({'employee_data': serializer.data, 'tokens': token_data}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Set default values if needed
        serializer.validated_data.setdefault('is_staff', True)

        # Validate password length again (just to be sure)
        password = serializer.validated_data.get('password')
        self.validate_password_length(password)

        # Validate password using Django's built-in validators
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError({'password': e.messages})

        # Create the employee (Waiter or Bartender)
        employee = serializer.save()

        # Generate a refresh token for the employee
        refresh = RefreshToken.for_user(employee)
        refresh_token = str(refresh)

        # Attach the refresh token to the employee instance
        employee.refresh_token = refresh_token

        # Use make_password to hash the password
        # employee.set_password(make_password(password))
        # employee.save()

        employee.set_password(serializer.validated_data['password'])
        employee.save()

        # Set the user_id in the session
        serializer.save()

        # Check user_type and create a profile if it's a Waiter or Bartender
        user_type = serializer.validated_data.get('user_type')
        if user_type in ['Waiter', 'Bartender']:
            # Create or retrieve the profile
            profile, created = get_or_create_profile(employee, user_type)

            # Check if the profile was created or already existed
            if created:
                # Extract the schedules data from the validated data
                schedules_data = serializer.validated_data.get(
                    'employee_schedules', [])

                # Create Schedule instances and associate them with the Profile
                for schedule_data in schedules_data:
                    day = schedule_data['day']
                    start_time = schedule_data['start_time']
                    end_time = schedule_data['end_time']

                    # Check if a similar schedule already exists
                    existing_schedule = EmployeeSchedule.objects.filter(
                        day=day, start_time=start_time, end_time=end_time, employee=employee).first()

                    if not existing_schedule:
                        # Create Schedule instance
                        schedule_instance = EmployeeSchedule.objects.create(
                            day=day, start_time=start_time, end_time=end_time, employee=employee)


def get_or_create_profile(user, user_type):
    if user_type == 'Waiter':
        return WaiterProfile.objects.get_or_create(user=user)[0], True
    elif user_type == 'Bartender':
        return BartenderProfile.objects.get_or_create(user=user)[0], True
    else:
        # Handle other user types if needed
        return None, False


class EmployeeListPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 100


class EmployeeList(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    pagination_class = EmployeeListPagination
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get a list of all employees",
        summary="List Employees",
        responses={200: EmployeeSerializer(many=True)}
    )
    def get_queryset(self):
        queryset = CustomUser.objects.all()

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(user_type__icontains=search_term)
            )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details, update, or delete an employee.",
        summary="Retrieve/Update/Delete Employee",
        responses={
            200: EmployeeSerializer,
            204: "No Content",
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update an employee.",
        summary="Update Employee",
        responses={200: EmployeeSerializer, 204: "No Content", }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        description="Delete an employee.",
        summary="Delete Employee",
        responses={204: "No Content", }
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# ===========================================================================
# BRANCH
# ===========================================================================
class BranchCreateView(generics.CreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Create a new branch.",
        summary="Create Branch",
        responses={201: BranchSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class BranchList(generics.ListCreateAPIView):
    serializer_class = BranchSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get a list of all branches",
        summary="List Branches",
        responses={200: BranchSerializer(many=True), 204: "No Content"}
    )
    def get_queryset(self):
        queryset = Branch.objects.all()

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            queryset = queryset.filter(
                Q(branch_name__icontains=search_term)
            )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BranchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details, update, or delete a branch.",
        summary="Retrieve/Update/Delete Branch",
        responses={
            200: BranchSerializer,
            204: "No Content",
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update a branch.",
        summary="Update Branch",
        responses={200: BranchSerializer, 204: "No Content", }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        description="Delete a branch.",
        summary="Delete Branch",
        responses={204: "No Content", }
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        existing_image = serializer.instance.image
        existing_schedules = serializer.instance.schedules
        serializer.save()

        if 'image' not in self.request.data or not self.request.data['image']:
            serializer.instance.image = existing_image
        if 'schedules' not in self.request.data or not self.request.data['schedules']:
            serializer.instance.schedules = existing_schedules
            serializer.instance.save()

# ===========================================================================
# ADMIN LOGIN
# ===========================================================================


class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the admin user
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            # Login the admin user
            login(request, user)

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)

            # Access the token using the `access_token` attribute
            access_token = refresh.access_token
            refresh_token = str(refresh)

            return Response({'access_token': str(access_token), 'refresh_token': refresh_token}, status=status.HTTP_200_OK)

        else:
            print("Authentication failed.")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# ===========================================================================
# CUSTOMER EMAIL CHECK
# ===========================================================================


class CustomerEmailCheckView(APIView):
    serializer_class = CustomerEmailSerializer

    @extend_schema(
        description="Check if customer's email is in the database and send a verification code.",
        summary="Customer Email Check",
        responses={200: "Email is taken",
                   201: "Verification code sent successfully."}
    )
    def post(self, request, *args, **kwargs):
        serializer = CustomerEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Check if the email is in the database
        if get_user_model().objects.filter(email=email).exists():
            return Response({'message': 'Email is taken'}, status=status.HTTP_200_OK)

        # Generate and send a 4-digit code
        confirmation_code = get_random_string(
            length=4, allowed_chars='1234567890')

        #
        confirmation_code = '4444'
        #

        # Set a flag in the user's session to indicate the need for confirmation
        request.session['pending_confirmation_user'] = {
            'data': serializer.validated_data,
            'confirmation_code': confirmation_code
        }

        # Send confirmation email
        subject = 'Welcome to Junior Project'
        message = f'This project is realized by the best team! Burte, Vlad, Nursultan, Aidana, Assyl\nYour verification code is: {
            confirmation_code}'
        from_email = 'assyl.akhambay@gmail.com'
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({'message': 'Verification code sent successfully.'}, status=status.HTTP_201_CREATED)

# ===========================================================================
# CUSTOMER REGISTRATION
# ===========================================================================


class CustomerRegistrationView(APIView):
    serializer_class = CustomerRegistrationSerializer

    @extend_schema(
        description="Register customer by adding to the database after providing email and confirmation code.",
        summary="Customer Registration",
        responses={201: "Customer registered successfully.",
                   400: "Invalid confirmation code."}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')

        # Retrieve user data from the session
        pending_user_data = request.session.get('pending_confirmation_user')

        if not pending_user_data:
            return Response({'error': 'User not found or not registered'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the provided confirmation code matches the stored code
        if confirmation_code != pending_user_data['confirmation_code']:
            return Response({'error': 'Invalid confirmation code.'}, status=status.HTTP_400_BAD_REQUEST)

        first_name = email.split('@')[0]
        pending_user_data['data']['first_name'] = first_name

        # Use the stored data to create the user
        serializer = CustomerRegistrationSerializer(
            data=pending_user_data['data'])
        serializer.is_valid(raise_exception=True)

        # Save user with the provided confirmation code as the password
        user = serializer.save(
            username=email, password=confirmation_code, user_type='customer')

        user.bonus_points = 100
        user.first_name = email.split('@')[0]
        user.save()

        # Authenticate the user and generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = jwt_encode(user)

        # Remove the session data after user creation
        request.session.pop('pending_confirmation_user', None)

        # Return response indicating successful registration along with tokens
        return Response({
            'message': 'Customer registered successfully.',
            'access_token': str(access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_201_CREATED)

# ===========================================================================
# CUSTOMER AUTHENTICATION CHECK
# ===========================================================================


class CustomerAuthenticationCheckView(APIView):
    serializer_class = CustomerAuthenticationCheckSerializer

    @extend_schema(
        description="Check if customer's email is in the database and send a new verification code.",
        summary="Customer Authentication Check",
        responses={200: "New verification code sent successfully.",
                   404: "User with this email is not registered."}
    )
    def post(self, request, *args, **kwargs):
        serializer = CustomerAuthenticationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Generate and send a new 4-digit code
        confirmation_code = get_random_string(
            length=4, allowed_chars='1234567890')

        #
        confirmation_code = '4444'
        #

        # Set a flag in the user's session to indicate the need for confirmation
        request.session['pending_confirmation_user'] = {
            'data': serializer.validated_data,
            'confirmation_code': confirmation_code
        }

        user = get_user_model().objects.filter(email=email).first()

        if user:
            user.confirmation_code = confirmation_code
            user.save()

            # Send confirmation email
            subject = 'Welcome to Junior Project'
            message = f'This project is realized by the best team! Burte, Vlad, Nursultan, Aidana, Assyl\nYour new verification code is: {
                confirmation_code}'
            from_email = 'assyl.akhambay@gmail.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'New verification code sent successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User with this email is not registered.'}, status=status.HTTP_404_NOT_FOUND)


User = get_user_model()

# ===========================================================================
# CUSTOMER AUTHENTICATION
# ===========================================================================


class CustomerAuthenticationView(APIView):
    serializer_class = CustomerLoginSerializer

    @extend_schema(
        description="Authenticate customer after providing email and confirmation code.",
        summary="Customer Authentication",
        responses={200: "Authentication successful.",
                   401: "Invalid credentials."}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')

        # Retrieve user data from the session
        pending_user_data = request.session.get('pending_confirmation_user')

        user = User.objects.filter(
            email=email, confirmation_code=confirmation_code).first()

        if user is not None:
            # Login the user
            login(request, user)
            update_last_login(None, user)

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)

            # Access the token using the `access_token` attribute
            access_token = refresh.access_token

            # Check if a CustomerProfile exists for the authenticated user
            try:
                customer_profile = CustomerProfile.objects.get(user=user)
            except CustomerProfile.DoesNotExist:
                # If not, create a CustomerProfile for the user
                customer_profile = CustomerProfile.objects.create(
                    user=user, email=user.email, first_name=user.first_name)

            return Response({
                'message': 'Authentication successful.',
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'customer_profile': CustomerProfileSerializer(customer_profile).data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


# ======================================================================
# BARTENDER AUTHENTICATION CHECK
# ======================================================================


class BartenderAuthenticationCheckView(APIView):
    serializer_class = BartenderAuthenticationCheckSerializer

    @extend_schema(
        description="Check if Bartender's email is in the database and send a confirmation code.",
        summary="Bartender Authentication Check",
        responses={200: "Confirmation code sent successfully.",
                   404: "Bartender with this email is not registered."}
    )
    def post(self, request, *args, **kwargs):
        serializer = BartenderAuthenticationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Generate and send a new 4-digit code
        confirmation_code = get_random_string(
            length=4, allowed_chars='1234567890')

        #
        confirmation_code = '4444'
        #

        # Set a flag in the user's session to indicate the need for confirmation
        request.session['pending_confirmation_user'] = {
            'data': serializer.validated_data,
            'confirmation_code': confirmation_code
        }

        user = get_user_model().objects.filter(email=email).first()

        if user:
            user.confirmation_code = confirmation_code
            user.save()

            # Send confirmation email
            subject = 'Login to Bartender\'s admin panel'
            message = f'Your confirmation code is: {
                confirmation_code}'
            from_email = 'assyl.akhambay@gmail.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'Confirmation code sent successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Bartender with this email is not registered.'}, status=status.HTTP_404_NOT_FOUND)

# ===========================================================================
# BARTENDER AUTHENTICATION
# ===========================================================================


class BartenderAuthenticationView(APIView):
    serializer_class = BartenderLoginSerializer

    @extend_schema(
        description="Authenticate bartender after providing email and confirmation code.",
        summary="Bartender Authentication",
        responses={200: "Authentication successful.",
                   401: "Invalid credentials."}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')

        # Retrieve user data from the session
        pending_user_data = request.session.get('pending_confirmation_user')

        user = User.objects.filter(
            email=email, confirmation_code=confirmation_code).first()

        if user is not None:
            # Login the user
            login(request, user)
            update_last_login(None, user)

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)

            # Access the token using the `access_token` attribute
            access_token = refresh.access_token
            return Response({
                'message': 'Authentication successful.',
                'access_token': str(access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

# ===========================================================================
# WAITER AUTHENTICATION CHECK
# ===========================================================================


class WaiterAuthenticationCheckView(APIView):
    serializer_class = WaiterAuthenticationCheckSerializer

    @extend_schema(
        description="Check if Waiter's email is in the database and send a confirmation code.",
        summary="Waiter Authentication Check",
        responses={200: "Confirmation code sent successfully.",
                   404: "Waiter with this email is not registered."}
    )
    def post(self, request, *args, **kwargs):
        serializer = WaiterAuthenticationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Generate and send a new 4-digit code
        confirmation_code = get_random_string(
            length=4, allowed_chars='1234567890')

        # Hardcoding confirmation code for testing
        confirmation_code = '4444'

        # Set a flag in the user's session to indicate the need for confirmation
        request.session['pending_confirmation_user'] = {
            'data': serializer.validated_data,
            'confirmation_code': confirmation_code
        }

        user = get_user_model().objects.filter(email=email).first()

        if user:
            user.confirmation_code = confirmation_code
            user.save()

            # Send confirmation email
            subject = 'Login to Waiter\'s admin panel'
            message = f'Your confirmation code is: {confirmation_code}'
            from_email = 'assyl.akhambay@gmail.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'Confirmation code sent successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Waiter with this email is not registered.'}, status=status.HTTP_404_NOT_FOUND)

# ===========================================================================
# WAITER AUTHENTICATION
# ===========================================================================


class WaiterAuthenticationView(APIView):
    serializer_class = WaiterLoginSerializer

    @extend_schema(
        description="Authenticate waiter after providing email and confirmation code.",
        summary="Waiter Authentication",
        responses={200: "Authentication successful.",
                   401: "Invalid credentials."}
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')

        # Retrieve user data from the session
        pending_user_data = request.session.get('pending_confirmation_user')

        user = User.objects.filter(
            email=email, confirmation_code=confirmation_code).first()

        if user is not None:
            # Login the user
            login(request, user)
            update_last_login(None, user)

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)

            # Access the token using the `access_token` attribute
            access_token = refresh.access_token
            return Response({
                'message': 'Authentication successful.',
                'access_token': str(access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

# ===========================================================================
# PROFILES
# ===========================================================================


class CustomerProfileView(generics.RetrieveAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    # permission_classes = [IsAuthenticated]
    lookup_field = 'user'

    @extend_schema(
        description="Retrieve details of a profile.",
        summary="Retrieve profile",
        responses={
            200: CustomerProfileSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CustomerProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    # permission_classes = [IsAuthenticated]
    lookup_field = 'user'

    @extend_schema(
        description="Get details, update, or delete a profile.",
        summary="Retrieve/Update/Delete profile",
        responses={
            200: CustomerProfileSerializer,
            204: "No Content",
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update a profile.",
        summary="Update profile",
        responses={200: BranchSerializer, 204: "No Content", }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        description="Delete operation is not allowed for profiles.",
        summary="Delete profile (Not Allowed)",
        responses={405: "Method Not Allowed", }
    )
    def delete(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if 'email' in request.data:
            return Response({'error': 'Email field cannot be modified'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class WaiterProfileView(generics.RetrieveAPIView):
    queryset = WaiterProfile.objects.all()
    serializer_class = WaiterProfileSerializer
    # permission_classes = [IsAuthenticated]
    lookup_field = 'user'

    @extend_schema(
        description="Retrieve details of a profile.",
        summary="Retrieve profile",
        responses={
            200: WaiterProfileSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class BartenderProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BartenderProfile.objects.all()
    serializer_class = BartenderProfileSerializer
    lookup_field = 'user'
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Retrieve details of a profile.",
        summary="Retrieve profile",
        responses={
            200: BartenderProfileSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
