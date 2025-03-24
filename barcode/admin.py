
from django.contrib import admin
from .models import MailItem

@admin.register(MailItem)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("barcode", "batch", "last_event_name")  # Jadvaldagi ustunlar
    list_filter = ("barcode","batch", "last_event_name")  # Filtr bo‘limi
    search_fields = ("barcode","batch", "last_event_name")  # Qidirish imkoniyati
