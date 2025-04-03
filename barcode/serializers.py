from rest_framework import serializers
from .models import MailItem
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import TemuUser

class MailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailItem
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemuUser
        fields = ['id', 'login', 'email']

class ObtainTokenSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(login=data['login'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return user