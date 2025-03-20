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
        raw_data = request.body  # JSON emas, oddiy Python dict bo‘lishi mumkin

        # Logga kelgan ma'lumotni yozish
        logger.info(f"Received raw data: {raw_data}")

        token_key = request.headers.get('Authorization')

        if not token_key:
            return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)

        if token_key != SECRET_API_TOKEN:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # 🔄 Python dict → JSON formatga o'tkazish
            if isinstance(raw_data, bytes):  # Agar `request.body` baytlar ko‘rinishida bo‘lsa
                raw_data = raw_data.decode("utf-8")

            if isinstance(raw_data, str):  # Agar JSON string bo‘lsa
                cleaned_data = json.loads(raw_data.replace("'", "\""))  # Bitta tirnoqlarni almashtirish
            else:
                cleaned_data = raw_data  # Agar `dict` bo‘lsa, to‘g‘ridan-to‘g‘ri ishlatish

            order_number = cleaned_data.get("order_number")

            if not order_number:
                return Response({'error': 'order_number is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Orderni yaratish yoki yangilash
            order, created = Order.objects.update_or_create(
                order_number=order_number,
                defaults=cleaned_data  
            )

            status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response(OrderSerializer(order).data, status=status_code)

        except json.JSONDecodeError as e:
            return Response({'detail': f'JSON parse error - {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': f'Unexpected error - {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)