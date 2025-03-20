from django.shortcuts import render
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from rest_framework import status
import logging
from django.conf import settings

logger = logging.getLogger('django')  # 'django' loggerini ishlatish

class OrderAPIView(APIView):
    def post(self, request):
        data = request.data
        logger.info(f"Received data: {data}")

        # Tokenni so‘rovdan olish
        token_key = data.get('token')

        if not token_key:
            return Response({'error': 'Token is required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Tokenni settings.py dagi qiymat bilan solishtirish
        if token_key != settings.SECRET_API_TOKEN:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)

        order_number = data.get('order_number')

        if not order_number:
            return Response({'error': 'order_number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Orderni yaratish yoki yangilash
        order, created = Order.objects.update_or_create(
            order_number=order_number,
            defaults={key: value for key, value in data.items() if key != "token"}  # Tokenni filter qilish
        )

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(OrderSerializer(order).data, status=status_code)