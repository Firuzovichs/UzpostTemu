from django.shortcuts import render
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from rest_framework import status
import logging
logger = logging.getLogger('django')  # 'django' loggerini ishlatish

class OrderAPIView(APIView):
    def post(self, request):
        data = request.data

        # Logga kelgan ma'lumotni yozish
        logger.info(f"Received data: {data}")

        order_number = data.get('order_number')

        if not order_number:
            return Response({'error': 'order_number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Order mavjud bo‘lsa, yangilaydi, yo‘q bo‘lsa, yaratadi
        order, created = Order.objects.update_or_create(
            order_number=order_number,
            defaults=data  # Barcha kelgan ma'lumotlarni yangilash
        )

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(OrderSerializer(order).data, status=status_code)