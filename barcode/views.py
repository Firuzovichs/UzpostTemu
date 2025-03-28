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
from collections import Counter
from django.db import models
from datetime import timedelta
from collections import Counter
from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MailItem
from django.db.models import Count


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
            
            mail_item.last_event_name.append(status_text)
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