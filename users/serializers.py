from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("name", "email", "password")

    def create(self, validated_data):
        user = Users(
            name=validated_data["name"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.save()
        return user


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
