import os
import logging

import asyncio
from metaapi_cloud_sdk import MetaApi
from datetime import datetime
from dotenv import load_dotenv
from django.conf import settings
from asgiref.sync import sync_to_async



from service.notifications import send_success_email, send_error_email
from users.models import User
from service.utils import create_transaction_history



logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()


async def meta_api_buy_synchronization(account_name, login, password, server_name, lot, stop_loss, target, client_id, transaction):
    token = os.getenv('TOKEN')
    symbol = os.getenv('SYMBOL')
    admin_email = settings.ADMIN_EMAIL
    api = MetaApi(token)
    try:
        # Add MetaTrader account
        accounts = await api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        account = None
        for item in accounts:
            if item.login == login and item.type.startswith('cloud'):
                account = item
                break
        if not account:
            print('not account')
            logger.info('Adding MT5 account to MetaApi', account_name, login, password, server_name )
            account = await api.metatrader_account_api.create_account(
                {
                    'name': account_name,
                    'type': 'cloud',
                    'login': login,
                    'password': password,
                    'server': server_name,
                    'platform': 'mt5',
                    'magic': 1000,
                }
            )
        else:
            logger.info('MT5 account already added to MetaApi')

        #  wait until account is deployed and connected to broker
        logger.info('Deploying account')
        await account.deploy()
        logger.info('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # connect to MetaApi API
        connection = account.get_streaming_connection()
        await connection.connect()

        # wait until terminal state synchronized to the local state
        logger.info('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized()

        # access local copy of terminal state
        logger.info('Testing terminal state access')
        terminal_state = connection.terminal_state
        logger.info('connected:', terminal_state.connected)
        logger.info('connected to broker:', terminal_state.connected_to_broker)
        logger.info('account information:', terminal_state.account_information)
        logger.info('positions:', terminal_state.positions)
        logger.info('orders:', terminal_state.orders)
        logger.info('specifications:', terminal_state.specifications)
        logger.info(f'{symbol} specification:', terminal_state.specification(symbol))

        # access history storage
        history_storage = connection.history_storage
        logger.info('deals:', history_storage.deals[-5:])
        logger.info('deals with id=1:', history_storage.get_deals_by_ticket('1'))
        logger.info('deals with positionId=1:', history_storage.get_deals_by_position('1'))
        logger.info(
            'deals for the last day:',
            history_storage.get_deals_by_time_range(
                datetime.fromtimestamp(datetime.now().timestamp() - 24 * 60 * 60), datetime.now()
            ),
        )

        logger.info('history orders:', history_storage.history_orders[-5:])
        logger.info('history orders with id=1:', history_storage.get_history_orders_by_ticket('1'))
        logger.info('history orders with positionId=1:', history_storage.get_history_orders_by_position('1'))
        logger.info(
            'history orders for the last day:',
            history_storage.get_history_orders_by_time_range(
                datetime.fromtimestamp(datetime.now().timestamp() - 24 * 60 * 60), datetime.now()
            ),
        )

        await connection.subscribe_to_market_data(symbol)
        logger.info(f'{symbol}price:', terminal_state.price(symbol))
        current_price = terminal_state.price(symbol) 

        logger.info(f'Current market price of {symbol}:', current_price)
        
        sl_price = current_price['bid'] - stop_loss
        tp_price = current_price['bid'] + target

         # Get the current market price
        print(tp_price,"tp_price")
        print(sl_price,'sl_price')
        try:
            print(f'Submitting market buy order for {lot} lots of {symbol}')
            result = await connection.create_market_buy_order(symbol, lot, sl_price, tp_price, {'comment': 'TARI-B',
                                                                          'clientId': client_id})
            print(result, 'result #####')

            order_id = result.get('orderId', '')
            print(f'Trade successful(BUY), order ID: {order_id}, result code is: {result["stringCode"]}')
            await sync_to_async(transaction.update_status)('COMPLETED')
            send_success_email(admin_email, 'BUY', symbol, order_id)
        except Exception as err:
            await connection.close()
            await account.undeploy()
            await sync_to_async(transaction.update_status)('FAILED')
            print(f'Trade failed with error: {api.format_error(err)}')
            send_error_email(admin_email, 'BUY', symbol, api.format_error(err))
    
        # finally, undeploy account after the test
        print('Undeploying MT5 account so that it does not consume any unwanted resources')
        await connection.close()
        await account.undeploy()

    except Exception as err:
        await connection.close()
        await account.undeploy()
        logger.error('BUY', api.format_error(err))


async def meta_api_sell_synchronization(account_name, login, password, server_name, lot, stop_loss, target, client_id, transaction):
    token = os.getenv('TOKEN')
    symbol = os.getenv('SYMBOL')
    admin_email = settings.ADMIN_EMAIL
    api = MetaApi(token)
    try:
        # Add MetaTrader account
        accounts = await api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        account = None
        for item in accounts:
            if item.login == login and item.type.startswith('cloud'):
                account = item
                break
        if not account:
            logger.info('Adding MT5 account to MetaApi', account_name, login, password, server_name )
            account = await api.metatrader_account_api.create_account(
                {
                    'name': account_name,
                    'type': 'cloud',
                    'login': login,
                    'password': password,
                    'server': server_name,
                    'platform': 'mt5',
                    'magic': 1000,
                }
            )
        else:
            logger.info('MT5 account already added to MetaApi')

        #  wait until account is deployed and connected to broker
        logger.info('Deploying account')
        await account.deploy()
        logger.info('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # connect to MetaApi API
        connection = account.get_streaming_connection()
        await connection.connect()

        # wait until terminal state synchronized to the local state
        logger.info('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized()

        # access local copy of terminal state
        logger.info('Testing terminal state access')
        terminal_state = connection.terminal_state
        logger.info('connected:', terminal_state.connected)
        logger.info('connected to broker:', terminal_state.connected_to_broker)
        logger.info('account information:', terminal_state.account_information)
        logger.info('positions:', terminal_state.positions)
        logger.info('orders:', terminal_state.orders)
        logger.info('specifications:', terminal_state.specifications)
        logger.info(f'{symbol} specification:', terminal_state.specification(symbol))

        # access history storage
        history_storage = connection.history_storage
        logger.info('deals:', history_storage.deals[-5:])
        logger.info('deals with id=1:', history_storage.get_deals_by_ticket('1'))
        logger.info('deals with positionId=1:', history_storage.get_deals_by_position('1'))
        logger.info(
            'deals for the last day:',
            history_storage.get_deals_by_time_range(
                datetime.fromtimestamp(datetime.now().timestamp() - 24 * 60 * 60), datetime.now()
            ),
        )

        logger.info('history orders:', history_storage.history_orders[-5:])
        logger.info('history orders with id=1:', history_storage.get_history_orders_by_ticket('1'))
        logger.info('history orders with positionId=1:', history_storage.get_history_orders_by_position('1'))
        logger.info(
            'history orders for the last day:',
            history_storage.get_history_orders_by_time_range(
                datetime.fromtimestamp(datetime.now().timestamp() - 24 * 60 * 60), datetime.now()
            ),
        )

        await connection.subscribe_to_market_data(symbol)
        logger.info(f'{symbol}price:', terminal_state.price(symbol))
        current_price = terminal_state.price(symbol) 

        logger.info(f'Current market price of {symbol}:', current_price)
        
        sl_price = current_price['bid'] + stop_loss
        tp_price = current_price['bid'] - target

         # Get the current market price
        print(tp_price,"tp_price")
        print(sl_price,'sl_price')
        try:
            print(f'Submitting market buy order for {lot} lots of {symbol}')
            result = await connection.create_market_sell_order(symbol, lot, sl_price, tp_price, {'comment': 'TRAI-S',
                                                                          'clientId': client_id})
            order_id = result.get('orderId', '')
            # Print the result
            print(f'Trade successful(BUY), order ID: {order_id}, result code is: {result["stringCode"]}')
            await sync_to_async(transaction.update_status)('COMPLETED')
            send_success_email(admin_email, 'SELL', symbol, order_id)  # Send success email
        except Exception as err:
            await connection.close()
            await account.undeploy()
            print(f'Trade failed with error: {api.format_error(err)}')
            await sync_to_async(transaction.update_status)('FAILED')
            send_error_email(admin_email, 'SELL', symbol, api.format_error(err))  # Send error email

        # finally, undeploy account after the test
        print('Undeploying MT5 account so that it does not consume any unwanted resources')
        await connection.close()
        await account.undeploy()

    except Exception as err:
        await connection.close()
        await account.undeploy()
        logger.error('BUY', api.format_error(err))



async def meta_api_close_positions_by_symbol(request_user_id):
    token = os.getenv('TOKEN')
    admin_email = settings.ADMIN_EMAIL
    symbol = os.getenv('SYMBOL')
    api = MetaApi(token)
    try:
        # Add MetaTrader account
        accounts = await api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        account = None
        for item in accounts:
            account = item
            user = await sync_to_async(User.objects.filter(username=account.login).first)()
            
            if not user:
                logger.error(f'User not found for account {account.login}')
                continue

            # Create transaction asynchronously
            transaction = await sync_to_async(create_transaction_history)(
                {'transaction_type': 'CLOSE', 'stop_loss': 0, 
                    'target': 0, 'open_price': 0, 'user': user.id if user else None,
                    'request_user_id': request_user_id
                }
            )
            # Wait until account is deployed and connected to broker
            logger.info('Deploying account')
            await account.deploy()
            logger.info('Waiting for API server to connect to broker (may take a couple of minutes)')
            await account.wait_connected()

            # Connect to MetaApi API
            connection = account.get_streaming_connection()
            await connection.connect()

            # Wait until terminal state synchronized to the local state
            logger.info('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
            await connection.wait_synchronized()

            # Access local copy of terminal state
            terminal_state = connection.terminal_state
            logger.info('connected:', terminal_state.connected)
            logger.info('connected to broker:', terminal_state.connected_to_broker)
            logger.info('account information:', terminal_state.account_information)
            logger.info('positions:', terminal_state.positions)
            logger.info('orders:', terminal_state.orders)

            # Close positions by symbol
            logger.info(f'Closing all positions for {symbol}')
            close_result = await connection.close_positions_by_symbol(symbol)
            print(close_result, 'result')

            if close_result['stringCode'] == "TRADE_RETCODE_DONE":
                logger.info(f'All positions for {symbol} closed successfully')
                await sync_to_async(transaction.update_status)('COMPLETED')
                send_success_email(admin_email, 'CLOSE', symbol)  # Send success email
                
            else:
                logger.error(f'Failed to close positions for {symbol}, result code: {close_result["stringCode"]}')
                await sync_to_async(transaction.update_status)('FAILED')
                send_error_email(admin_email, 'CLOSE', symbol, close_result['stringCode'])  # Send error email

            # Finally, undeploy account after the task
            logger.info('Undeploying MT5 account so that it does not consume any unwanted resources')
            await connection.close()
            await account.undeploy()
        else:
            logger.error('Unable to fetch accounts')

    except Exception as err:
        await connection.close()
        await account.undeploy()
        logger.error('CLOSE', api.format_error(err))
