from django.urls import path, include
from .views import (EmployeeCreateView, EmployeeList, EmployeeDetail, AdminLoginView,
                    BranchCreateView, BranchList, BranchDetail,
                    CustomerEmailCheckView, CustomerRegistrationView,
                    CustomerAuthenticationCheckView, CustomerAuthenticationView)
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('cafe/admin/login/', AdminLoginView.as_view(),
         name='cafe_admin_login'),
    # TokenObtainPairView

    path('employee/add/', EmployeeCreateView.as_view(), name='employee'),
    path('employee/all/', EmployeeList.as_view(), name='employee_list'),
    path('employee/<int:pk>/', EmployeeDetail.as_view(), name='employee_detail'),

    path("auth/", include("rest_framework.urls")),
    path("ignore/this/", include("dj_rest_auth.urls")),

    path('branch/add/', BranchCreateView.as_view(), name='branch'),
    path('branch/all/', BranchList.as_view(), name='branch_list'),
    path('branch/<int:pk>/', BranchDetail.as_view(), name='branch_detail'),

    path('customer/check-email-register/',
         CustomerEmailCheckView.as_view(), name='customer_email_register'),
    path('customer/register/', CustomerRegistrationView.as_view(),
         name='customer_register'),
    path('customer/check-email-login/',
         CustomerAuthenticationCheckView.as_view(), name='customer_email_login'),
    path('customer/login/', CustomerAuthenticationView.as_view(),
         name='customer_login'),
]
