from django.db import models

class Order(models.Model):
    history_id = models.BigIntegerField(unique=True)
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=1000, null=True, blank=True)
    cod_status = models.CharField(max_length=1000, null=True, blank=True)
    status_desc = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    customer_id = models.BigIntegerField(null=True, blank=True)
    courier = models.CharField(max_length=1000, null=True, blank=True)
    transaction_id = models.BigIntegerField(null=True, blank=True)
    driver = models.CharField(max_length=1000, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    order_id = models.BigIntegerField(null=True, blank=True)
    warehouse_id = models.BigIntegerField(null=True, blank=True)
    warehouse_name = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"{self.order_number} - {self.status} - {self.warehouse_name}"