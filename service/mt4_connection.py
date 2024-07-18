import os
import asyncio
from metaapi_cloud_sdk import MetaApi
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('TOKEN') 
login = os.getenv('MT4_LOGIN') 
password = os.getenv('MT4_PASSWORD')
server_name = os.getenv('MT4_SERVER') 
account_ame = os.getenv('MT4_ACCOUNT_NAME')


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
            print('Adding MT4 account to MetaApi')
            account = await api.metatrader_account_api.create_account(
                {
                    'name': account_ame,
                    'type': 'cloud',
                    'login': login,
                    'password': password,
                    'server': server_name,
                    'platform': 'mt4',
                    'magic': 1000,
                }
            )
        else:
            print('MT4 account already added to MetaApi')

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
        print('EURUSD specification:', terminal_state.specification('EURUSD'))

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

        await connection.subscribe_to_market_data('EURUSD')
        print('EURUSD price:', terminal_state.price('EURUSD'))

        # calculate margin required for trade
        print(
            'margin required for trade',
            await connection.calculate_margin(
                {'symbol': 'GBPUSD', 'type': 'ORDER_TYPE_BUY', 'volume': 0.1, 'openPrice': 1.1}
            ),
        )

        # trade
        print('Submitting pending order')
        try:
            result = await connection.create_limit_buy_order(
                'GBPUSD', 0.07, 1.0, 0.9, 2.0, {'comment': 'comm', 'clientId': 'TE_GBPUSD_7hyINWqAlE'}
            )
            print('Trade successful, result code is ' + result['stringCode'])
        except Exception as err:
            print('Trade failed with error:')
            print(api.format_error(err))

        # finally, undeploy account after the test
        print('Undeploying MT4 account so that it does not consume any unwanted resources')
        await connection.close()
        await account.undeploy()

    except Exception as err:
        # process errors
        if hasattr(err, 'details'):
            # returned if the server file for the specified server name has not been found
            # recommended to check the server name or create the account using a provisioning profile
            if err.details == 'E_SRV_NOT_FOUND':
                print(err)
            # returned if the server has failed to connect to the broker using your credentials
            # recommended to check your login and password
            elif err.details == 'E_AUTH':
                print(err)
            # returned if the server has failed to detect the broker settings
            # recommended to try again later or create the account using a provisioning profile
            elif err.details == 'E_SERVER_TIMEZONE':
                print(err)
        print(api.format_error(err))
    exit()


asyncio.run(meta_api_synchronization())