from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from .tasks import sell_operation_task, buy_operation_task, close_operation_task
from .models import TransactionHistory

class SellOperationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        args = request.data
        args['request_user_id'] = request.user.id
        # Trigger Celery task for sell operation
        sell_operation_task.delay(**args)
        return Response({'message': 'Sell operation initiated'}, status=status.HTTP_200_OK)


class BuyOperationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        args = request.data
        args['request_user_id'] = request.user.id
        # Trigger Celery task for buy operation
        buy_operation_task.delay(**args)
        return Response({'message': 'Buy operation initiated'}, status=status.HTTP_200_OK)


class CloseOperationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        args= {
        'request_user_id': request.user.id
        }
        has_buy_or_sell_transactions = TransactionHistory.objects.filter(
            transaction_type__in=['BUY', 'SELL']
        ).exists()
        if not has_buy_or_sell_transactions:
            return Response({'message': 'No BUY or SELL transactions found'}, status=status.HTTP_400_BAD_REQUEST)
        # Trigger Celery task for buy operation
        close_operation_task.delay(**args)
        return Response({'message': 'Close operation initiated'}, status=status.HTTP_200_OK)


