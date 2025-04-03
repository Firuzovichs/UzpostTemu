from rest_framework import serializers
from .models import MailItem
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class MailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailItem
        fields = "__all__"
