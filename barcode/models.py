from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin,Group, Permission

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, first_name, last_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(phone_number, first_name, last_name, password, **extra_fields)

    def get_by_natural_key(self, phone_number):
        return self.get(phone_number=phone_number)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()
    groups = models.ManyToManyField(
        Group, 
        related_name='customuser_set',  # Bu yerda related_name qo'shildi
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        Permission, 
        related_name='customuser_permissions_set',  # Bu yerda related_name qo'shildi
        blank=True
    )
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'customuser'
        verbose_name = "Foydalanuvchilar"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ('id',)
        indexes = [
            models.Index(fields=['id', 'phone_number']),
        ]

    def str(self):
        return self.phone_number
    
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
