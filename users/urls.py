from django.urls import path, include
from .views import (obtain_jwt_token, EmployeeCreateView, EmployeeList, EmployeeDetail,
                    BranchCreateView, BranchList, BranchDetail, CustomerEmailCheckView,
                    CustomerLoginView, AdminLoginView, AdminLoginView5)
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('cafe/admin/login/', AdminLoginView5.as_view(),
         name='cafe_admin_login'),
    # TokenObtainPairView

    path('employee/add/', EmployeeCreateView.as_view(), name='employee'),
    path('employee/all/', EmployeeList.as_view(), name='employee'),
    path('employee/<int:pk>/', EmployeeDetail.as_view(), name='employee'),

    path("auth/", include("rest_framework.urls")),
    path("cafeshka/admin/", include("dj_rest_auth.urls")),

    path('branch/add/', BranchCreateView.as_view(), name='branch'),
    path('branch/all/', BranchList.as_view(), name='branch'),
    path('branch/<int:pk>/', BranchDetail.as_view(), name='branch'),

    path('customer/register/', CustomerEmailCheckView.as_view(), name='register_user'),
    path('customer/login/', CustomerLoginView.as_view(), name='customer_login'),
]
