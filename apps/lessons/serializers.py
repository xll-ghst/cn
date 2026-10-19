from rest_framework import serializers
from .models import Lesson

class LessonSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "created_by", "created_at")
        read_only_fields = ("id", "created_by", "created_at")
