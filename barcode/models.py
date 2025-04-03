from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin,Group, Permission

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone number must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    password = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    # Customize groups and user_permissions with related_name to avoid clashes
    groups = models.ManyToManyField(
        Group, 
        related_name="customuser_set",  # Updated related_name
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        Permission, 
        related_name="customuser_permissions_set",  # Updated related_name
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

    def __str__(self):
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
