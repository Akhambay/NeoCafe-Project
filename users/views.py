from django.db.models import F
import logging
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import (
    CustomerEmailSerializer, CustomerRegistrationSerializer, CustomerLoginSerializer,
    CustomerAuthenticationCheckSerializer, EmployeeAddSerializer, BranchEditSerializer,
    BranchSerializer, EmployeeSerializer, ScheduleSerializer, EmployeeScheduleSerializer,
    BartenderAuthenticationCheckSerializer, BartenderLoginSerializer,
    WaiterAuthenticationCheckSerializer, WaiterLoginSerializer,
    CustomerProfileSerializer, EmployeeProfileSerializer, CustomerSerializer,
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
from django.middleware.csrf import get_token
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

def create_employee_profile(employee, user_type, schedules_data, profile_model):
    # Create or retrieve profile
    employee_profile, created = profile_model.objects.get_or_create(
        user=employee)

    # Check if the profile was created or already existed
    if created:
        # Create Schedule instances and associate them with the profile
        for schedule_data in schedules_data:
            day = schedule_data['day']
            start_time = schedule_data['start_time']
            end_time = schedule_data['end_time']

            # Create Schedule instance
            schedule_instance = EmployeeSchedule.objects.create(
                day=day, start_time=start_time, end_time=end_time, employee=employee_profile)

    return employee_profile


class EmployeeCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeAddSerializer

    def validate_password_length(self, password):
        if not (4 <= len(password) <= 10):
            return Response({'error': 'Password must be between 4 and 10 characters.'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        employee, profile_id = self.perform_create(serializer)

        refresh = RefreshToken.for_user(serializer.instance)
        token_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        headers = self.get_success_headers(serializer.data)

        # Add user_id and profile_id to the response
        user_id = employee.id
        response_data = {
            'employee_data': serializer.data,
            'tokens': token_data,
            'user_id': user_id,
            'profile_id': profile_id,  # Include profile_id in the response
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Set default values if needed
        serializer.validated_data.setdefault('is_staff', True)

        # Validate password length again (just to be sure)
        password = serializer.validated_data.get('password')
        if not (4 <= len(password) <= 10):
            raise ValidationError(
                {'error': 'Password must be between 4 and 10 characters.'})

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

        # Check user_type and create a profile if it's a Waiter or Bartender
        user_type = serializer.validated_data.get('user_type')
        profile = None
        if user_type == 'Waiter':
            profile = WaiterProfile.objects.create(user=employee)
        elif user_type == 'Bartender':
            profile = BartenderProfile.objects.create(user=employee)

        # Retrieve profile_id after creating the profile
        profile_id = profile.id if profile else None

        return employee, profile_id

    def get_or_create_profile(self, user, user_type):
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
        queryset = CustomUser.objects.filter(
            user_type__in=['Waiter', 'Bartender']
        )

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)
        branch_name = self.request.query_params.get('branch_name', None)

        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(user_type__icontains=search_term)
            )

        if branch_name:
            branch = get_object_or_404(Branch, branch_name=branch_name)
            queryset = queryset.filter(branch=branch)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CustomerList(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    pagination_class = EmployeeListPagination
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get a list of all customers",
        summary="List Customers",
        responses={200: CustomerSerializer(many=True)}
    )
    def get_queryset(self):
        queryset = CustomUser.objects.filter(
            user_type__in=['Customer', 'customer']
        )

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
    queryset = CustomUser.objects.filter(
        user_type__in=['Waiter', 'Bartender']
    )
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


class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.filter(
        user_type__in=['Customer', 'customer']
    )
    serializer_class = CustomerSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details, update, or delete an customer.",
        summary="Retrieve/Update/Delete Customer",
        responses={
            200: CustomerSerializer,
            204: "No Content",
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update an customer.",
        summary="Update customer",
        responses={200: CustomerSerializer, 204: "No Content", }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        description="Delete an customer.",
        summary="Delete customer",
        responses={204: "No Content", }
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# ===========================================================================
# BRANCH
# ===========================================================================


class BranchListPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


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
    pagination_class = BranchListPagination
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get a list of all branches",
        summary="List Branches",
        responses={200: BranchSerializer(many=True), 204: "No Content"}
    )
    def get_queryset(self):
        queryset = Branch.objects.all().order_by(F('id').desc())

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            queryset = queryset.filter(
                Q(branch_name__icontains=search_term)
            )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Pagination
        paginator = BranchListPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = self.get_serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class BranchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchEditSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


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
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({
                'message': 'Confirmation code sent successfully.',
                'bartender_email': user.email
            }, status=status.HTTP_200_OK)
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
        description="Check if Waiter's username is in the database and send a confirmation code.",
        summary="Waiter Authentication Check",
        responses={200: "Confirmation code sent successfully.",
                   404: "Waiter with this username is not registered."}
    )
    def post(self, request, *args, **kwargs):
        serializer = WaiterAuthenticationCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate and send a new 4-digit code
        confirmation_code = get_random_string(
            length=4, allowed_chars='1234567890')

        # Hardcoding confirmation code for testing
        confirmation_code = '4444'

        # Set a flag in the user's session to indicate the need for confirmation
        request.session['pending_confirmation_user'] = {
            'user_id': user.id,
            'confirmation_code': confirmation_code
        }

        # Save the confirmation code in the user model
        user.confirmation_code = confirmation_code
        user.save()

        # Send confirmation email
        subject = 'Login to Waiter\'s admin panel'
        message = f'Your confirmation code is: {confirmation_code}'
        from_email = 'assyl.akhambay@gmail.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        csrf_token = get_token(request)

        return Response({
            'message': 'Confirmation code sent successfully.',
            'waiter_email': user.email,
            'csrf_token': get_token(request)
        }, status=status.HTTP_200_OK)


# ===========================================================================
# WAITER AUTHENTICATION
# ===========================================================================
class WaiterAuthenticationView(APIView):
    serializer_class = WaiterLoginSerializer

    @extend_schema(
        description="Authenticate waiter after providing username and confirmation code.",
        summary="Waiter Authentication",
        responses={200: "Authentication successful.",
                   401: "Invalid credentials."}
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = WaiterLoginSerializer(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data['user']
            branch_id = user.branch.id
            user_id = user.id
            # profile_id = user.profile.id

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'message': 'Authentication successful.',
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'branch_id': branch_id,
                'user_id': user_id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    lookup_field = 'user_id'

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
