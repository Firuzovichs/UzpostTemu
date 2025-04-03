from rest_framework import serializers
from .models import MailItem
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

class MailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailItem
        fields = "__all__"

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'first_name', 'last_name', 'is_active', 'is_staff')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class TokenObtainPairSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")
        
        user = CustomUser.objects.get(phone_number=phone_number)
        
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return {'access': access_token, 'refresh': str(refresh)}
        else:
            raise serializers.ValidationError("Invalid phone number or password.")

