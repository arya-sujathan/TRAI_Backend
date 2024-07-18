from rest_framework import serializers
from .models import TradeSignal

class TradeSignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeSignal
        fields = '__all__'
