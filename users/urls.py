from django.urls import path, include
from .views import obtain_jwt_token, EmployeeCreateView, EmployeeList, EmployeeDetail, UserLoginView

urlpatterns = [
    # ... other patterns
    path('login/', obtain_jwt_token, name='admin_login'),
    path('employee/add/', EmployeeCreateView.as_view(), name='employee'),
    path('employee/all/', EmployeeList.as_view(), name='employee'),
    path('employee/<int:pk>/', EmployeeDetail.as_view(), name='employee'),
    path("auth/", include("rest_framework.urls")),
    path("cafe/admin/", include("dj_rest_auth.urls")),
]
