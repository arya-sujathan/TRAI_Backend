from django.contrib import admin
from .models import User, Broker

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('serialno', 'username', 'email', 'date_of_registration', 'is_active', 'is_staff')
    search_fields = ('serialno', 'username', 'email')
    list_filter = ('is_active', 'is_staff')
    readonly_fields = ('date_of_registration',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'email', 'whatsapp_number', 'plain_password', 'serialno', 'account_name')
        }),
        ('Broker Information', {
            'fields': ('broker', 'server_id', 'lot_size', 'token')
        }),
        ('Date Information', {
            'fields': ('date_of_registration', 'date_of_expiry')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff')
        }),
    )

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

