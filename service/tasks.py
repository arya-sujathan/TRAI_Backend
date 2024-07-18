import os
import asyncio
from celery import shared_task
from users.models import User
from service.meta_api_views import meta_api_sell_synchronization, meta_api_buy_synchronization, meta_api_close_positions_by_symbol
from service.utils import create_transaction_history


@shared_task
def sell_operation_task(**kwargs):
    active_users = User.objects.filter(is_active=True, is_superuser=False)
    stop_loss = float(kwargs.get('stopLoss'))
    target = float(kwargs.get('target'))
    open_price = float(kwargs.get('openPrice', 0))
    request_user_id = kwargs.get('request_user_id')
    
    for user in active_users:
      
        transaction =create_transaction_history({
                'transaction_type': 'SELL', 'stop_loss': stop_loss, 
                'target': target, 'open_price': open_price,'user':user.id,
                'request_user_id': request_user_id
                }).client_id
        client_id = transaction.client_id
        asyncio.run(meta_api_sell_synchronization(user.account_name, user.username, user.plain_password, user.server_id, float(user.lot_size), stop_loss, target, client_id, transaction))


@shared_task
def buy_operation_task(**kwargs):
    active_users = User.objects.filter(is_active=True, is_superuser=False)
    stop_loss = float(kwargs.get('stopLoss'))
    target = float(kwargs.get('target'))
    open_price = float(kwargs.get('openPrice', 0))
    request_user_id = kwargs.get('request_user_id')
    
    for user in active_users:
        transaction =create_transaction_history({
                'transaction_type': 'BUY', 'stop_loss': stop_loss, 
                'target': target, 'open_price': open_price,'user':user.id,
                'request_user_id': request_user_id
                })
        client_id = transaction.client_id
            
        asyncio.run(meta_api_buy_synchronization(user.account_name, user.username, user.plain_password, user.server_id, float(user.lot_size), stop_loss, target, client_id, transaction))


@shared_task
def close_operation_task(**kwargs):
        request_user_id = kwargs.get('request_user_id')
        asyncio.run(meta_api_close_positions_by_symbol(request_user_id))