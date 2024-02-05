from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from .models import CustomUser, Branch
from .serializers import CustomUserSerializer, EmployeeSerializer, BranchSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


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
