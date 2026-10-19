from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import GoogleCodeSerializer
from .services import login_or_create_google_user

class EmailTokenObtainPairView(TokenObtainPairView):
    """SimpleJWT использует USERNAME_FIELD модели — в нашем случае email."""
    permission_classes = [AllowAny]

class EmailTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = login_or_create_google_user(serializer.validated_data["code"])
        return Response(result, status=status.HTTP_200_OK)
