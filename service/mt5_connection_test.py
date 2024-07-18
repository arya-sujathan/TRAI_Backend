import os
import asyncio
from metaapi_cloud_sdk import MetaApi
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
login = os.getenv('MT5_LOGIN')
password = os.getenv('MT5_PASSWORD')
server_name = os.getenv('MT5_SERVER_NAME')
account_name = os.getenv('MT5_ACCOUNT_NAME')

async def meta_api_synchronization():
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
            print('Adding MT5 account to MetaApi')
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
            print('MT5 account already added to MetaApi')

        #  wait until account is deployed and connected to broker
        print('Deploying account')
        await account.deploy()
        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # connect to MetaApi API
        connection = account.get_streaming_connection()
        await connection.connect()

        # wait until terminal state synchronized to the local state
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized()

        # access local copy of terminal state
        print('Testing terminal state access')
        terminal_state = connection.terminal_state
        print('connected:', terminal_state.connected)
        print('connected to broker:', terminal_state.connected_to_broker)
        print('account information:', terminal_state.account_information)
        print('positions:', terminal_state.positions)
        print('orders:', terminal_state.orders)
        print('specifications:', terminal_state.specifications)
        print('EURUSD specification:', terminal_state.specification('GOLD'))

        # access history storage
        history_storage = connection.history_storage
        print('deals:', history_storage.deals[-5:])
        print('deals with id=1:', history_storage.get_deals_by_ticket('1'))
        print('deals with positionId=1:', history_storage.get_deals_by_position('1'))
        print(
            'deals for the last day:',
            history_storage.get_deals_by_time_range(
                datetime.fromtimestamp(datetime.now().timestamp() - 24 * 60 * 60), datetime.now()
            ),
        )

        print('history orders:', history_storage.history_orders[-5:])
        print('history orders with id=1:', history_storage.get_history_orders_by_ticket('1'))
        print('history orders with positionId=1:', history_storage.get_history_orders_by_position('1'))
        print(
            'history orders for the last day:',
            history_storage.get_history_orders_by_time_range(
                datetime.fromtimestamp(datetime.now().timestamp() - 24 * 60 * 60), datetime.now()
            ),
        )

        await connection.subscribe_to_market_data('XAUUSDm')
        print('XAUUSDm price:', terminal_state.price('XAUUSDm'))

        # Market Execution Trade
        symbol = 'XAUUSDm'
        volume = 0.01 # Note: Ensure volume is a float, not a string
        # Example values (replace with your strategy)
        current_price = terminal_state.price(symbol) 
        print('Current market price of XAUUSDm:', current_price)

        # sell
        sl_price = current_price['bid'] + 4.00
        tp_price = current_price['bid'] - 5.00

        # # buy
        # sl_price = current_price['bid'] - 4.00
        # tp_price = current_price['bid'] + 5.00

        # lot = 0.01, 0.02
        

        # Get the current market price
        print(tp_price,"tp_price")
        print(sl_price,'sl_price')
        try:
            print(f'Submitting market buy order for {volume} lots of {symbol}')
            result = await connection.create_market_sell_order(symbol, 0.01, sl_price, tp_price, {'comment': 'comment',
                                                                          'clientId': f'TE_{symbol}_7hyIN12'})
            print(result, 'result')

            order_id = result.get('orderId')

            # Print the result
            print(f'Trade successful, order ID: {order_id}, result code is: {result["stringCode"]}')
        except Exception as err:
            await connection.close()
            await account.undeploy()
            print(f'Trade failed with error: {api.format_error(err)}')
            
        # Optional: Set Stop Loss and Take Profit (if needed)
        if result["stringCode"] == "TRADE_RETCODE_PLACED":
            order_id = result['orderId']

            # ... (your SL/TP code as before) ...
            # Example:
            # sl_price = current_price - 0.05 # SL at 0.05 loss
            # tp_price = current_price + 0.10 # TP at 0.10 profit
            # await connection.create_stop_loss_order(order_id, sl_price)  
            # await connection.create_take_profit_order(order_id, tp_price)

        # finally, undeploy account after the test
        print('Undeploying MT5 account so that it does not consume any unwanted resources')
        await connection.close()
        await account.undeploy()

    except Exception as err:
        await connection.close()
        await account.undeploy()
        # process errors
        print(api.format_error(err))
    exit()


asyncio.run(meta_api_synchronization())