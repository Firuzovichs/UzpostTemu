from rest_framework import serializers
from .models import MailItem
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

class MailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailItem
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']  # Kerakli maydonlarni qo'shing

