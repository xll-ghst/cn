from rest_framework.generics import ListCreateAPIView
from apps.users.permissions import IsTeacherOrReadOnly
from .models import Lesson
from .serializers import LessonSerializer

class LessonListCreateView(ListCreateAPIView):
    queryset = Lesson.objects.select_related("created_by").all().order_by("-created_at")
    serializer_class = LessonSerializer
    permission_classes = [IsTeacherOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
