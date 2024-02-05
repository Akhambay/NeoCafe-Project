from django.urls import path, include
from .views import obtain_jwt_token, EmployeeCreateView, EmployeeList, EmployeeDetail, UserLoginView, BranchCreateView, BranchList, BranchDetail, CustomerEmailCheckView, CustomerLoginView

urlpatterns = [
    path('login/', obtain_jwt_token, name='admin_login'),
    path('employee/add/', EmployeeCreateView.as_view(), name='employee'),
    path('employee/all/', EmployeeList.as_view(), name='employee'),
    path('employee/<int:pk>/', EmployeeDetail.as_view(), name='employee'),

    path("auth/", include("rest_framework.urls")),
    path("cafe/admin/", include("dj_rest_auth.urls")),

    path('branch/add/', BranchCreateView.as_view(), name='branch'),
    path('branch/all/', BranchList.as_view(), name='branch'),
    path('branch/<int:pk>/', BranchDetail.as_view(), name='branch'),

    path('customer/register/', CustomerEmailCheckView.as_view(), name='register_user'),
    path('customer/login/', CustomerLoginView.as_view(), name='customer_login'),
]
