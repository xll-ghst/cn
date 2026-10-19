from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView
from .models import User
from .permissions import IsTeacherOrReadOnly

class PermissionProbe(APIView):
    permission_classes = [IsTeacherOrReadOnly]

class IsTeacherOrReadOnlyTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PermissionProbe.as_view()
        self.student = User.objects.create_user(email="student@example.com", password="Testpass123!")
        self.teacher = User.objects.create_user(email="teacher@example.com", password="Testpass123!", role="teacher")

    def test_anonymous_cannot_read(self):
        request = self.factory.get("/")
        response = self.view(request)
        self.assertEqual(response.status_code, 401)

    def test_student_can_read(self):
        request = self.factory.get("/")
        force_authenticate(request, user=self.student)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_post(self):
        request = self.factory.post("/", {}, format="json")
        force_authenticate(request, user=self.student)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)

    def test_teacher_can_post(self):
        request = self.factory.post("/", {}, format="json")
        force_authenticate(request, user=self.teacher)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
