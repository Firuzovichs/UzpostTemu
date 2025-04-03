from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractUser

class TemuUser(AbstractUser):
    login = models.CharField(max_length=255, unique=True)  # username o‘rniga
    email = models.EmailField(unique=True,default=None)  # Email majburiy
    password = models.CharField(max_length=255,blank=False)

    USERNAME_FIELD = 'login'  # Django login uchun `login` ni ishlatadi
    REQUIRED_FIELDS = ['email']  # Superuser yaratishda talab qilinadigan maydonlar

    # related_name qo'shish
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='temuuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='temuuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def __str__(self):
        return self.login

class MailItem(models.Model):
    batch = models.CharField(max_length=255, null=True, blank=True)  # ✅ Bo‘sh bo‘lishi mumkin
    barcode = models.CharField(max_length=50, unique=True)  # Majburiy
    weight = models.FloatField()  # Majburiy
    send_date = models.DateTimeField(null=True, blank=True)  # ✅ Bo‘sh bo‘lishi mumkin
    received_date = models.DateTimeField(null=True, blank=True)
    last_event_date = models.DateTimeField(null=True, blank=True)
    last_event_name = models.JSONField(default=list)  
    city = models.CharField(max_length=150, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ So‘nggi yangilangan vaqt

    def __str__(self):
        return f"{self.batch} - {self.barcode}"
