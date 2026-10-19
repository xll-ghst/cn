from rest_framework import serializers
from .models import User

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role")

class GoogleCodeSerializer(serializers.Serializer):
    code = serializers.CharField(trim_whitespace=True)
