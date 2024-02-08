from users.serializers import CustomerEmailSerializer, CustomerRegistrationSerializer, CustomerLoginSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import (
    CustomerEmailSerializer,
    CustomerRegistrationSerializer,
    CustomerLoginSerializer, CustomerSerializer, CustomerAuthenticationCheckSerializer,
    EmployeeAddSerializer, BranchSerializer, EmployeeSerializer,
)

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView
from dj_rest_auth.serializers import JWTSerializer, TokenSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from .models import CustomUser, Branch, Customer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
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
from .serializers import AdminLoginSerializer
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


obtain_jwt_token = CustomTokenObtainPairView.as_view()


def generate_unique_username(email):
    username_prefix = email.split('@')[0]

    # Generate a random string to ensure uniqueness
    random_suffix = get_random_string(length=4)

    unique_username = f"{username_prefix}_{random_suffix}"

    return unique_username


class AdminLoginTokenView(TokenObtainPairView):
    serializer_class = AdminLoginSerializer


# EMPLOYEE
class EmployeeCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeAddSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Create a new employee.",
        summary="Create Employee",
        responses={201: EmployeeAddSerializer, 204: "No Content", }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        refresh = RefreshToken.for_user(serializer.instance)
        token_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        headers = self.get_success_headers(serializer.data)
        return Response({'employee_data': serializer.data, 'tokens': token_data}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Create the employee

        employee = serializer.save()

        # Generate a refresh token for the employee
        refresh = RefreshToken.for_user(employee)
        refresh_token = str(refresh)

        # Attach the refresh token to the employee instance
        employee.refresh_token = refresh_token
        employee.set_password(serializer.validated_data['password'])
        employee.save()

        # Set the user_id in the session
        self.request.session['pending_confirmation_user'] = employee.id
        # Save the session to persist the changes
        self.request.session.save()

####


class EmployeeList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer

    @extend_schema(
        description="Get a list of all employees",
        summary="List Employees",
        responses={200: EmployeeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer

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


# BRANCH
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
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    @extend_schema(
        description="Get a list of all branches",
        summary="List Branches",
        responses={200: BranchSerializer(many=True), 204: "No Content"}
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BranchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

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
        serializer.save()

        if 'image' not in self.request.data or not self.request.data['image']:
            serializer.instance.image = existing_image
            serializer.instance.save()

# ADMIN LOGIN


class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Retrieve user data from the session
        user_data = request.session.get('pending_confirmation_user')

        if not user_data or 'data' not in user_data:
            return Response({'error': 'Admin not found or not registered'}, status=status.HTTP_400_BAD_REQUEST)

        user_data = user_data['data']
        user_id = user_data.get('id')

        if user_id is None:
            return Response({'error': 'Admin not found or not registered'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            return Response({'error': 'Admin not found or not registered'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the user's password explicitly
        user = authenticate(request, username=username, password=password)

        # Check if the provided confirmation code now matches the user's password
        if user is not None:
            # Login the user
            login(request, user)
            update_last_login(None, user)

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)

            # Access the token using the `access_token` attribute
            access_token = refresh.access_token
            return Response({'token': str(access_token)}, status=status.HTTP_200_OK)
        else:
            print("Authentication failed.")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# CustomerRegistration


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

        # Use the stored data to create the user
        serializer = CustomerRegistrationSerializer(
            data=pending_user_data['data'])
        serializer.is_valid(raise_exception=True)

        # Save user with the provided confirmation code as the password
        user = serializer.save(
            username=email, password=confirmation_code, user_type='customer')

        # Remove the session data after user creation
        request.session.pop('pending_confirmation_user', None)

        # Return response indicating successful registration
        return Response({'message': 'Customer registered successfully.'}, status=status.HTTP_201_CREATED)


class CustomerAuthenticationCheckView(APIView):
    serializer_class = CustomerLoginSerializer

    @extend_schema(
        description="Check if customer's email is in the database and send a verification code.",
        summary="Customer Authentication Check",
        responses={200: "Email is taken, new verification code sent successfully.",
                   404: "User with this email is not registered."}
    )
    def post(self, request, *args, **kwargs):
        serializer = CustomerEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Check if the email is in the database
        user_exists = get_user_model().objects.filter(email=email).exists()

        if user_exists:
            # Generate and send a new 4-digit code
            confirmation_code = get_random_string(
                length=4, allowed_chars='1234567890')

            # Set a flag in the user's session to indicate the need for confirmation
            request.session['pending_confirmation_user'] = {
                'data': serializer.validated_data,
                'confirmation_code': confirmation_code
            }

            # Send confirmation email
            subject = 'Welcome to Junior Project'
            message = f'This project is realized by the best team! Burte, Vlad, Nursultan, Aidana, Assyl\nYour new verification code is: {
                confirmation_code}'
            from_email = 'assyl.akhambay@gmail.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({'message': 'Email is taken, new verification code sent successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User with this email is not registered.'}, status=status.HTTP_404_NOT_FOUND)


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

        if not pending_user_data:
            return Response({'error': 'User not found or not registered'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the provided confirmation code matches the stored code
        if confirmation_code != pending_user_data['confirmation_code']:
            return Response({'error': 'Invalid confirmation code.'}, status=status.HTTP_400_BAD_REQUEST)

        # Use the stored data to create the user
        serializer = CustomerLoginSerializer(
            data=pending_user_data['data'])
        serializer.is_valid(raise_exception=True)

        # Authenticate the user
        user = authenticate(request, username=email,
                            password=confirmation_code)

        if user is not None:
            # Login the user
            login(request, user)
            update_last_login(None, user)

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)

            # Access the token using the `access_token` attribute
            access_token = refresh.access_token
            return Response({'message': 'Authentication successful.', 'token': str(access_token)}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
