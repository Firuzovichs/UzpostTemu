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
        raw_data = request.data  # JSON emas, oddiy dict

        # Logga kelgan ma'lumotni yozish
        logger.info(f"Received raw data: {raw_data}")

        token_key = request.headers.get('Authorization')

        if not token_key:
            return Response({'error': 'Authorization header is required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Tokenni settings.py dagi qiymat bilan solishtirish
        if token_key != SECRET_API_TOKEN:
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)

        # ✅ Kelgan ma'lumotni JSON formatiga o‘tkazish (rekursiv)
        def convert_to_json_compatible(obj):
            if isinstance(obj, dict):
                return {str(k): convert_to_json_compatible(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_compatible(v) for v in obj]
            elif obj is None:
                return None  # yoki "null" agar string sifatida kerak bo‘lsa
            return obj

        # 🔄 Python dict → JSON formatdagi dict
        cleaned_data = convert_to_json_compatible(raw_data)

        order_number = cleaned_data.get("order_number")

        if not order_number:
            return Response({'error': 'order_number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Order mavjud bo‘lsa, yangilaydi, yo‘q bo‘lsa, yaratadi
        order, created = Order.objects.update_or_create(
            order_number=order_number,
            defaults=cleaned_data  
        )

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(OrderSerializer(order).data, status=status_code)