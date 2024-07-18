from django.db import models


class TradeSignal(models.Model):
    symbol = models.CharField(max_length=10)
    trade_type = models.CharField(max_length=4)  # 'buy' or 'sell'
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
