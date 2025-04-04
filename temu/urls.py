"""
URL configuration for temu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from barcode.views import MailItemAPIView,MailItemUpdateStatus,BatchStatisticsAPIView,MailItemAllListView,BarcodeInfoView,BatchStatsView,MyTokenObtainPairView,UploadFilesView
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("mail-items/", MailItemAPIView.as_view(), name="mail-items"),
    path("barcodes-info/", BarcodeInfoView.as_view(), name="barcode-info"),
    path('api/v1/order/',MailItemUpdateStatus.as_view(), name="update-status"),
    path("batch-statistics/", BatchStatisticsAPIView.as_view(), name="batch-statistics"),
    path("barcode-all/", MailItemAllListView.as_view(), name="barcode-all"),
    path('batch-stats/', BatchStatsView.as_view(), name='batch-stats'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('upload/', UploadFilesView.as_view(), name='upload_files'),
]
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'xml'])

