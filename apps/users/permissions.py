from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsTeacherOrReadOnly(BasePermission):
    """
    GET/HEAD/OPTIONS разрешены только авторизованным пользователям.
    Изменяющие запросы разрешены только пользователям с ролью teacher.
    """

    message = "Для изменения уроков нужна роль teacher."

    def has_permission(self, request, view):
        user = request.user

        # По ТЗ даже чтение недоступно анонимным пользователям.
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return getattr(user, "role", None) == "teacher"
