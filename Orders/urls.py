from django.contrib import admin
from django.urls import path
from data.views import OrderAPIView
urlpatterns = [
    path('api/v1/admin_login/', admin.site.urls),
    path('api/v1/order/', OrderAPIView.as_view(), name='order-api'),
]
