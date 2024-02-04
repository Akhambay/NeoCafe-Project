from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny


class AdministratorLogin(TokenObtainPairView):
    permission_classes = [AllowAny]


obtain_jwt_token = AdministratorLogin.as_view()
