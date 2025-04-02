import xml.etree.ElementTree as ET
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MailItem
from .serializers import MailItemSerializer
from rest_framework_xml.parsers import XMLParser  
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
import threading
import time
import requests
import json
from rest_framework.pagination import PageNumberPagination
from collections import Counter
from django.db import models
from datetime import timedelta
from collections import Counter
from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MailItem
from django.db.models import Count
from django.utils.timezone import now
class BarcodeInfoView(APIView):
    def post(self, request):
        barcodes = request.data.get("barcodes", [])
        
        if not isinstance(barcodes, list) or len(barcodes) > 10:
            return Response({"error": "Barcodes must be a list with a maximum of 10 items."}, status=status.HTTP_400_BAD_REQUEST)
        
        login_url = 'https://prodapi.pochta.uz/api/v1/customer/authenticate?context=customer'
        login_data = {
            'username': '075584875543',  # Foydalanuvchi nomini kiriting
            'password': 'Admin1234'   # Parolni kiriting
        }
        headers = {'Content-Type': 'application/json'}

        try:
            login_response = requests.post(login_url, headers=headers, data=json.dumps(login_data))
            login_response.raise_for_status()
            login_data = login_response.json()
            id_token = login_data.get('data', {}).get('id_token')
        except requests.RequestException as e:
            return Response({"error": "Failed to authenticate", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_headers = {
            'Authorization': f'Bearer {id_token}',
            'Content-Type': 'application/json'
        }

        results = []
        for barcode in barcodes:
            try:
                user_url = f'https://prodapi.pochta.uz/api/v1/customer/orders?page=0&size=20&state=all&use_solr=true&refresh=false&with_totals=true&search_type=order_number&status=completed&search={barcode}'
                user_response = requests.get(user_url, headers=user_headers)
                user_response.raise_for_status()
                user_data = user_response.json()
                user_list = user_data.get('data', {}).get('list', [])
                user_id = user_list[0].get('id') if user_list else None

                if not user_id:
                    results.append({"barcode": barcode, "error": "Not found"})
                    continue
                
                another_api_url = f'https://prodapi.pochta.uz/api/v1/customer/order/{user_id}/mobile'
                another_response = requests.get(another_api_url, headers=user_headers)
                another_response.raise_for_status()
                another_data = another_response.json()

                results.append({
                    "barcode": barcode,
                    "recipient_signature_url": another_data.get('data', {}).get('actual_recipient_signature'),
                    "recipient_card_url": another_data.get('data', {}).get('actual_recipient_id_card'),
                    "name": another_data.get('data', {}).get('recipient_data', {}).get('customer', {}).get('name', "Noma'lum"),
                    "address": another_data.get('data', {}).get('recipient_data', {}).get('address', "Noma'lum"),
                    "last_status_date": another_data.get('data', {}).get('last_status_date', "Noma'lum")
                })
            except requests.RequestException as e:
                results.append({"barcode": barcode, "error": "Request failed", "details": str(e)})

        return Response(results, status=status.HTTP_200_OK)
class MailItemPagination(PageNumberPagination):
    page_size = 10  # Har bir sahifada nechta mail item ko‘rsatilishini belgilash
    page_size_query_param = 'page_size'  # So'rov parametri orqali sahifa o'lchamini belgilash imkoniyati
    max_page_size = 100  # Maksimal sahifa o'lchami


class MailItemAllListView(APIView):
    def get(self, request):
        mail_items = MailItem.objects.order_by('-updated_at')
        
        paginator = MailItemPagination()  # Pagination obyektini yaratish
        paginated_mail_items = paginator.paginate_queryset(mail_items, request)  # Querysetni sahifalash
        
        serializer = MailItemSerializer(paginated_mail_items, many=True)
        
        # Sahifalangan javobni qaytarish
        return paginator.get_paginated_response(serializer.data)
    
class MailItemListView(APIView):
    def get(self, request):
        mail_items = MailItem.objects.order_by('-updated_at')[:6]  # Oxirgi 6 ta yozuvni olish
        data = []
        
        for item in mail_items:
            last_event_index = len(item.last_event_name) - 1 if item.last_event_name else None
            data.append({
                "barcode": item.barcode,
                "weight": item.weight,
                "send_date": item.send_date,
                "received_date": item.received_date,
                "last_event_date": item.last_event_date,
                "last_event_name": item.last_event_name[last_event_index] if last_event_index is not None else None,
                "city": item.city,
            })
        
        return Response(data, status=status.HTTP_200_OK)



class BatchStatisticsAPIView(APIView):
    def get(self, request):
        # Barcha batchlar bo‘yicha weight yig‘indisini hisoblash
        batch_stats = (
    MailItem.objects.values("batch")
    .annotate(total_count=Count("barcode"))  # Har bir batch bo‘yicha barcode soni
)

        # Har bir batch uchun natijani saqlash
        result = {}

        for batch in batch_stats:
            batch_name = batch["batch"]
            total_count = batch["total_count"]

            # Ushbu batchdagi barcha MailItem obyektlarini olish
            items = MailItem.objects.filter(batch=batch_name)

            # Statuslarni hisoblash uchun Counter
            status_counter = Counter()

            # Oxirgi statuslarni hisoblash
            for item in items:
                if item.last_event_name:  # List bo‘sh bo‘lmasa
                    last_status = item.last_event_name[-1]  # Oxirgi elementni olish
                    status_counter[last_status] += 1

            # Natijalarni batch bo‘yicha saqlash
            result[batch_name] = {
                "total_count": total_count,
                "status_counts": status_counter  # Har bir batch uchun statuslar
            }

        return Response({"batch_statistics": result})

    




class MailItemUpdateStatus(APIView):
    def post(self, request):
        data = request.data
        
        barcode = data.get("order_number") 
        warehouse_name = data.get("warehouse_name") 
        status_text = data.get("status")  
        event_date = parse_datetime(data.get("date"))  

        try:
            mail_item = MailItem.objects.get(barcode=barcode)

            mail_item.city = warehouse_name  
            if status_text == "unassigned":
                mail_item.last_event_name.append(status_text)
                mail_item.received_date = event_date
                mail_item.last_event_date = event_date
                mail_item.save(update_fields=['city', 'last_event_name','received_date', 'last_event_date','updated_at'])

            if status_text == "sent_to_customs":
                mail_item.last_event_name.append(status_text)
                mail_item.last_event_date = event_date
            if status_text == "returned_from_customs":
                mail_item.last_event_name.append(status_text)
                mail_item.last_event_date = event_date
                mail_item.save(update_fields=['city', 'last_event_name', 'last_event_date', 'updated_at'])

                def update_to_send_to_domestic_location():
                    try:
                        delayed_mail_item = MailItem.objects.get(barcode=barcode)
                        delayed_mail_item.last_event_name.append("send_to_domestic_location")
                        delayed_mail_item.last_event_date = now()
                        delayed_mail_item.save(update_fields=['last_event_name', 'last_event_date', 'updated_at'])

                        def update_to_receive_at_delivery_office():
                            try:
                                final_mail_item = MailItem.objects.get(barcode=barcode)
                                final_mail_item.last_event_name.append("receive_at_delivery_office")
                                final_mail_item.last_event_date = now()
                                final_mail_item.save(update_fields=['last_event_name', 'last_event_date', 'updated_at'])
                            except MailItem.DoesNotExist:
                                pass

                        # 5 daqiqa (300 sekund) kutib yangi statusni qo'shish
                        timer_2 = threading.Timer(300, update_to_receive_at_delivery_office)
                        timer_2.start()

                    except MailItem.DoesNotExist:
                        pass  

                timer_1 = threading.Timer(600, update_to_send_to_domestic_location)
                timer_1.start()
            if status_text == "out_for_delivery":
                mail_item.last_event_name.append(status_text)
                mail_item.last_event_date = event_date
            if status_text == "ready_for_delivery":
                mail_item.last_event_name.append(status_text)
                mail_item.last_event_date = event_date
            if status_text == "completed" or status_text == "issued_to_recipient":
                mail_item.last_event_name.append("completed")
                mail_item.last_event_date = event_date


            
            mail_item.save(update_fields=['city', 'last_event_name', 'last_event_date','updated_at'])

            return Response({"message": "MailItem updated successfully"}, status=200)


        except MailItem.DoesNotExist:
            return Response({"error": f"MailItem with barcode {barcode} not found"}, status=status.HTTP_404_NOT_FOUND)







class MailItemAPIView(APIView):
    parser_classes = [XMLParser]  

    def post(self, request):
        xml_data = request.body.decode("utf-8")  
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        namespaces = {'ips': 'http://upu.int/ips'}  

        mail_items = root.findall(".//ips:MailItem", namespaces)

        for item in mail_items:
            barcode = item.get("ItemId")  

            # ✅ Agar barcode allaqachon bazada mavjud bo‘lsa, xatolik qaytariladi
            if MailItem.objects.filter(barcode=barcode).exists():
                return Response(
                    {"error": f"Barcode {barcode} already exists!"},
                    status=400
                )

            batch_element = item.find("ips:Misc1", namespaces)
            batch = batch_element.text if batch_element is not None else None

            weight_element = item.find("ips:ItemWeight", namespaces)
            weight = float(weight_element.text) if weight_element is not None else 0.0

            send_date_element = item.find("ips:ItemEvent/ips:Date", namespaces)
            send_date = parse_datetime(send_date_element.text) if send_date_element is not None else None

            first_status_element = item.find("ips:ItemEvent/ips:TNCd",namespaces)
            first_status = first_status_element.text if first_status_element is not None else None
            last_event_name = ["On way"] if first_status == "1261" else []

            try:
                mail_item = MailItem.objects.create(
                    barcode=barcode,
                    batch=batch,
                    weight=weight,
                    send_date=send_date,
                    last_event_name=last_event_name
                )
            except IntegrityError:
                return Response(
                    {"error": f"Duplicate entry for barcode {barcode}"},
                    status=400
                )

        return Response({"message": "Data saved successfully"}, status=201)