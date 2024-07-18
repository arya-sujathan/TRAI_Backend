from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    
    def _create_user(self, password, username, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.plain_password = password
        user.save()
        return user

    def create_superuser(self, password, username, **extra_fields):
        print(extra_fields)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(password, username, **extra_fields)
    
class Broker(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Broker Name', help_text='Enter the name of the broker')
    is_active = models.BooleanField(default=True, verbose_name='Active', help_text='Designates whether this broker is active')

class User(AbstractBaseUser, PermissionsMixin):
    serialno = models.CharField(max_length=100, verbose_name='Serial Number', help_text='Enter the serial number')
    username = models.CharField(max_length=150, unique=True, verbose_name='Username', help_text='Enter the username')
    email = models.EmailField(verbose_name='Email', help_text='Enter the email address', blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='WhatsApp Number', help_text='Enter the WhatsApp number')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Broker', help_text='Select the broker')
    server_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Server ID', help_text='Enter the server ID')
    date_of_registration = models.DateTimeField(default=timezone.now, verbose_name='Date of Registration', help_text='Date and time of user registration')
    date_of_expiry = models.DateTimeField(blank=True, null=True, verbose_name='Date of Expiry', help_text='Date and time of user expiry')
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Lot Size', help_text='Enter the lot size')
    plain_password = models.CharField(max_length=128, blank=True, null=True, verbose_name='Plain Password', help_text='Enter the plain text password')
    token = models.TextField(verbose_name='Token', help_text='Enter the token (more than 300 characters)', blank=True, null=True)
    platform = models.CharField(max_length=255, verbose_name='Platform', help_text='Enter the platform')
    account_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Account Name', help_text='Enter the account name')
    
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='created_users', blank=True, null=True)
    modified_by = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='modified_users', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True, verbose_name='Active', help_text='Designates whether this user is active')
    is_staff = models.BooleanField(default=False, verbose_name='Staff Status', help_text='Designates whether the user can access the admin site')
    is_superuser = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def set_plain_password(self, password):
        self.plain_password = password
        self.set_password(password)  # This sets the hashed password
    
    def get_full_name(self):
        """Returns the full name of the user."""
        return self.username

    def has_expired(self):
        """Checks if the user's registration has expired."""
        return self.date_of_expiry is not None and self.date_of_expiry < timezone.now()

    def __str__(self):
        return self.username
