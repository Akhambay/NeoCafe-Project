# urls.py

from django.urls import path
from .views import obtain_jwt_token

urlpatterns = [
    # ... other patterns
    path('login/', obtain_jwt_token, name='admin_login'),
]
