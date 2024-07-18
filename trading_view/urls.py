from django.urls import path
from .views import TradingViewWebhookListener

urlpatterns = [
    path('webhook/', TradingViewWebhookListener.as_view(), name='webhook_listener'),
]
