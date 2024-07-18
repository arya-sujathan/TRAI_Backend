
import os
import uuid
from django.db import models
from django.utils import timezone
from users.models import User
from django.db import transaction
from dotenv import load_dotenv

load_dotenv()
class TransactionHistory(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('CLOSE', 'Close')
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed')
    ]

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name='Transaction Type', help_text='Enter the transaction type (BUY or SELL)')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name='Status', help_text='Enter the status of the transaction')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Date and time of transaction creation')
    modified_on = models.DateTimeField(auto_now=True, verbose_name='Modified On', help_text='Date and time of last modification')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_transactions', blank=True, null=True, verbose_name='Created By', help_text='User who created this transaction')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='modified_transactions', blank=True, null=True, verbose_name='Modified By', help_text='User who last modified this transaction')
    client_id = models.CharField(max_length=255, verbose_name='Client ID', help_text='Enter the unique ID', unique=True, blank=True)
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Stop Loss', help_text='Enter the stop loss value')
    target = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Target', help_text='Enter the target value')
    open_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Open Price', help_text='Enter the open price')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', verbose_name='User', help_text='User who owns this transaction', blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.transaction_type} - {self.status}"

    @transaction.atomic
    def update_status(self, new_status):
        """ Atomically updates the status of the transaction. """
        try:
            self.status = new_status
            self.save()
        except Exception as err:
            # Handle other exceptions that might occur during save
            print(f"Error occurred while updating status: {err}")



    @classmethod
    def generate_client_id(cls):
        """Generates a unique client ID in the TE_SYMBOL_uniqueID format."""
        unique_id = uuid.uuid4().hex.upper()[:8] 
        symbol = os.getenv('SYMBOL')
        prefix = f"TE_{symbol}_"
        return f"{prefix}{unique_id}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.client_id:
            # Only set the client_id if it hasn't been set yet
            self.client_id = self.generate_client_id()
        super(TransactionHistory, self).save(*args, **kwargs)