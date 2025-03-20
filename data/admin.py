from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "status", "warehouse_name")  # Jadvaldagi ustunlar
    list_filter = ("status", "warehouse_name")  # Filtr bo‘limi
    search_fields = ("order_number", "warehouse_name")  # Qidirish imkoniyati
