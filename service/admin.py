from django.contrib import admin
from .models import TransactionHistory

class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_type', 'status', 'created_at', 'modified_on', 'created_by', 'modified_by', 'client_id', 'stop_loss', 'target', 'open_price', 'user')
    list_filter = ('transaction_type', 'status', 'created_at', 'user')
    search_fields = ('id', 'client_id', 'user__username')
    readonly_fields = ('created_at', 'modified_on', 'client_id')

    fieldsets = (
        (None, {
            'fields': ('transaction_type', 'status', 'client_id', 'user')
        }),
        ('Details', {
            'fields': ('stop_loss', 'target', 'open_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_on')
        }),
        ('User Information', {
            'fields': ('created_by', 'modified_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set created_by on new objects
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(TransactionHistory, TransactionHistoryAdmin)
