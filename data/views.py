from django.shortcuts import render
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from rest_framework import status
import logging
from django.conf import settings
import json
SECRET_API_TOKEN = "asdkl;fj;lkasdfj8ifuh4uf-a1561***766#22$%^&*lkjhgfcdgbhj158"
logger = logging.getLogger('django')  # 'django' loggerini ishlatish

class OrderAPIView(APIView):
    def post(self, request):
        logger.info(f"Received data: {request.data}")  

        # Tokenni Header orqali olish
        token_key = request.headers.get('Authorization')

        if not token_key:
            return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Tokenni settings.py dagi qiymat bilan solishtirish
        if token_key != SECRET_API_TOKEN:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)

        try:
            raw_data = request.data  

            # None qiymatlarini null bilan almashtirish
            def convert_none_to_null(obj):
                if isinstance(obj, dict):
                    return {k: convert_none_to_null(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_none_to_null(v) for v in obj]
                elif obj is None:
                    return ""  # yoki "null", agar null sifatida saqlash kerak bo'lsa
                return obj
            
            cleaned_data = convert_none_to_null(raw_data)

            order_number = cleaned_data.get('order_number')

            if not order_number:
                return Response({'error': 'order_number is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Orderni yaratish yoki yangilash
            order, created = Order.objects.update_or_create(
                order_number=order_number,
                defaults=cleaned_data  
            )

            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(OrderSerializer(order).data, status=status_code)

        except Exception as e:
            return Response({'detail': f'Error - {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)