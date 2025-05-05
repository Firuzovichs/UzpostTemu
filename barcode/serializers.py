from rest_framework import serializers
from .models import MailItem
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

class MailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailItem
        fields = "__all__"


class TokenObtainPairSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = get_user_model().objects.get(phone_number=phone_number)
        
        if user and user.check_password(password):
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return {'access': str(refresh.access_token), 'refresh': str(refresh)}
        else:
            raise serializers.ValidationError("Invalid phone number or password.")

class CityBarcodeCountSerializer(serializers.Serializer):
    city = serializers.CharField()
    barcode_count = serializers.IntegerField()