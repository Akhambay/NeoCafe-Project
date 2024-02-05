# from .utils import generate_unique_username
from rest_framework import status
# from dj_rest_auth.views.registration import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from .models import CustomUser, Branch, Customer
from .serializers import CustomUserSerializer, EmployeeSerializer, BranchSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomerSerializer
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


def generate_unique_username(email):
    username_prefix = email.split('@')[0]

    # Generate a random string to ensure uniqueness
    random_suffix = get_random_string(length=4)

    unique_username = f"{username_prefix}_{random_suffix}"

    return unique_username


class AdministratorLogin(TokenObtainPairView):
    permission_classes = [AllowAny]


obtain_jwt_token = AdministratorLogin.as_view()

###############


class UserLoginView(TokenObtainPairView):
    serializer_class = CustomUserSerializer

# EMPLOYEE


class EmployeeCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


class EmployeeList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = EmployeeSerializer

    def perform_update(self, serializer):
        existing_avatar = serializer.instance.avatar
        serializer.save()

        if 'avatar' not in self.request.data or not self.request.data['avatar']:
            serializer.instance.avatar = existing_avatar
            serializer.instance.save()


# BRANCH
class BranchCreateView(generics.CreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    # permission_classes = [IsAuthenticated]

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


class BranchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def perform_update(self, serializer):
        existing_image = serializer.instance.image
        serializer.save()

        if 'image' not in self.request.data or not self.request.data['image']:
            serializer.instance.image = existing_image
            serializer.instance.save()

# CustomerRegistration


class CustomerEmailCheckView(RegisterView):
    serializer_class = CustomerSerializer

    def create(self, request, *args, **kwargs):
        # Generate and send a 4-digit code
        confirmation_code = get_random_string(
            length=4, allowed_chars='1234567890')
        email = request.data.get('email')
        unique_username = generate_unique_username(email)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save user without password
        user = serializer.save(username=unique_username)
        user.set_password(confirmation_code)
        user.save()

        # Send confirmation email
        subject = 'Welcome to Junior Project'
        message = f'This project is realized by the best team! Burte, Vlad, Nursultan, Aidana, Assyl\nYour verification code is: {
            confirmation_code}'
        from_email = 'assyl.akhambay@gmail.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        # Authenticate the user
        authenticated_user = authenticate(
            request, username=user.username, password=confirmation_code)

        if authenticated_user is not None:
            # Login the user
            login(request, authenticated_user)
            update_last_login(None, authenticated_user)

            # Generate JWT token
            refresh = TokenModel.objects.create(user=authenticated_user)
            token = jwt_encode(refresh)

            return Response({'token': str(token)}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Authentication failed.'}, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()


class CustomerLoginView(TokenObtainPairView):
    serializer_class = CustomerSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        confirmation_code = request.data.get('confirmation_code')

        # Authenticate the user
        user = authenticate(request, email=email, password=confirmation_code)

        if user is not None:
            # Login the user
            login(request, user)

            # Check if the user already has a token
            refresh = RefreshToken.for_user(user)

            # Access the token using the `access_token` attribute
            access_token = refresh.access_token
            return Response({'token': str(access_token)}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
