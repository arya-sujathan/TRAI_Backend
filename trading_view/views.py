import logging
import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)
import logging
import json
from django.http import JsonResponse
from .serializers import TradeSignalSerializer
# from .trading import execute_trade
from rest_framework.response import Response


logger = logging.getLogger(__name__)

class TradingViewWebhookListener(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.body.decode('utf-8')
        
        # Get the client's IP address
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if ip_address:
            # The HTTP_X_FORWARDED_FOR header is a comma-separated list of IP addresses.
            # The first one is the client's IP.
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR', None)
        
        webhook_url = request.build_absolute_uri()
        logger.info(
            "TradingView webhook received at {} with data: {} from IP: {}".format(
                webhook_url,
                data,
                ip_address
            )
        )
        print("Webhook URL:", webhook_url)  # Print the URL of the webhook
        print("Webhook Data:", data)  # Print the data received from the webhook
        print("Webhook IP Address:", ip_address)  # Print the IP address of the request
        print("Webhook meta:", request.META)
        serializer = TradeSignalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Execute trade using MetaApi
            # execute_trade(serializer.validated_data)
            return Response(serializer.data, status=201)
        
        return JsonResponse({"message": "Webhook received successfully"})
