import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def google_code_to_profile(code: str) -> dict:
    """Обменивает одноразовый authorization code на профиль Google."""

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET or not settings.GOOGLE_REDIRECT_URI:
        raise ValidationError("Google OAuth не настроен на сервере.")

    try:
        token_response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )
        if token_response.status_code != 200:
            raise AuthenticationFailed("Не удалось подтвердить Google authorization code.")

        token_data = token_response.json()
        google_access_token = token_data.get("access_token")
        if not google_access_token:
            raise AuthenticationFailed("Google не вернул access token.")

        profile_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_access_token}"},
            timeout=10,
        )
        if profile_response.status_code != 200:
            raise AuthenticationFailed("Не удалось получить профиль Google.")

        profile = profile_response.json()
    except requests.RequestException:
        raise AuthenticationFailed("Сервис Google временно недоступен.")

    email = profile.get("email", "").strip().lower()
    # Не создаём аккаунт по непроверенному адресу.
    if not email or profile.get("verified_email") is not True:
        raise AuthenticationFailed("Google email отсутствует или не подтверждён.")

    return {"email": email}


def login_or_create_google_user(code: str) -> dict:
    """Находит/создаёт локального пользователя и выдаёт пару JWT."""

    profile = google_code_to_profile(code)
    user, is_new_user = User.objects.get_or_create(
        email=profile["email"],
        defaults={"role": User.Role.STUDENT},
    )

    if not user.is_active:
        raise AuthenticationFailed("Аккаунт отключён.")

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "is_new_user": is_new_user,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
    }
