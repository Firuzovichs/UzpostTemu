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
        data = json.dumps(request.data)
        logger.info(f"Received data: {data}")
        # Tokenni Header orqali olish
        token_key = request.headers.get('Authorization')

        if not token_key:
            return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Tokenni settings.py dagi qiymat bilan solishtirish
        if token_key != SECRET_API_TOKEN:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)

        order_number = data.get('order_number')

        if not order_number:
            return Response({'error': 'order_number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Orderni yaratish yoki yangilash
        order, created = Order.objects.update_or_create(
            order_number=order_number,
            defaults=data  # Barcha kelgan ma'lumotlarni yangilash
        )

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(OrderSerializer(order).data, status=status_code)