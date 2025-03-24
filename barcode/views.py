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
from datetime import timedelta

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

            if status_text:
                mail_item.last_event_name.append(status_text)

            if status_text == "Order Received":
                mail_item.received_date = event_date

            mail_item.last_event_date = event_date

            mail_item.save(update_fields=["city", "last_event_name", "received_date", "last_event_date", "updated_at"])
            if status_text == "Return from customs":
                threading.Thread(target=self.delayed_update1, args=(barcode,)).start()

            return Response({"message": "MailItem updated successfully"}, status=200)


        except MailItem.DoesNotExist:
            return Response({"error": f"MailItem with barcode {barcode} not found"}, status=status.HTTP_404_NOT_FOUND)
    def delayed_update1(self, barcode):
        time.sleep(600) 

        try:
            mail_item = MailItem.objects.get(barcode=barcode)
            mail_item.last_event_name.append("Send to domestic location")
            mail_item.last_event_date += timedelta(minutes=10)
            mail_item.save(update_fields=['last_event_name', 'last_event_date', 'updated_at'])
            threading.Thread(target=self.delayed_update2, args=(barcode,)).start()
        except MailItem.DoesNotExist:
            pass
    def delayed_update2(self, barcode):
        time.sleep(300) 

        try:
            mail_item = MailItem.objects.get(barcode=barcode)
            mail_item.last_event_name.append("Send to domestic location")
            mail_item.last_event_date += timedelta(minutes=5)
            mail_item.save(update_fields=['last_event_name', 'last_event_date', 'updated_at'])
        except MailItem.DoesNotExist:
            pass   


























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