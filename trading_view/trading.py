import asyncio
import os
from metaapi_cloud_sdk import MetaStats
from metaapi_cloud_sdk import MetaApi


token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIwMjhkNDk0ZDg0MWYxOWVlYTBlNmI2Yzg1M2FhMzk2YiIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZXN0LWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1ycGMtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTp3czpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6Im1ldGFzdGF0cy1hcGkiLCJtZXRob2RzIjpbIm1ldGFzdGF0cy1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiKjokVVNFUl9JRCQ6KiJdfSx7ImlkIjoicmlzay1tYW5hZ2VtZW50LWFwaSIsIm1ldGhvZHMiOlsicmlzay1tYW5hZ2VtZW50LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJjb3B5ZmFjdG9yeS1hcGkiLCJtZXRob2RzIjpbImNvcHlmYWN0b3J5LWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19LHsiaWQiOiJtdC1tYW5hZ2VyLWFwaSIsIm1ldGhvZHMiOlsibXQtbWFuYWdlci1hcGk6cmVzdDpkZWFsaW5nOio6KiIsIm10LW1hbmFnZXItYXBpOnJlc3Q6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbIio6JFVTRVJfSUQkOioiXX0seyJpZCI6ImJpbGxpbmctYXBpIiwibWV0aG9kcyI6WyJiaWxsaW5nLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyIqOiRVU0VSX0lEJDoqIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjAyOGQ0OTRkODQxZjE5ZWVhMGU2YjZjODUzYWEzOTZiIiwiaWF0IjoxNzE2OTk0MDc5fQ.FsEb-pqWXJV_Ok-1y09GCn_QpkbdQnybIXGzldwipgiu_OvAhZ7vaznTF1SBUTaIyAmana4qIKBTNevhD-5minpfJjwDyY26lJZEq1iqsDns8cDYa0wpxAzcWr3blemRatPpVYAXmX4KTogOL3b4JUJQ5C_bHgKo5UJA12Gdn1X56VvlE9dC_UfDpHMSgtxWboNibVQ-gqWNh9apGOcDSh4itpQe9YCz0KTt97dx5sVpar77o1uqOiOByZlrboSSUw30Xz6Cz5bVNfQjf0HDi2Q31CJrd5DfN-k3UAro5nUJ3bpVwjBsZxe2g35JIu0cQ3Qrr6R9XAby4zYFVGJaYzBQp6wIHCl7ov0e_GVHELs_nQBoyPw0HvzIKPwNAKp2nJn66jJWeErxqWPfD-LDanHznJi3dAlh0IwQbgIDM1o2-2QLt8s0JbVQPqihZpcxwZVIynqdn5flfLAFPUCMK6YYCR4t8ZQCL6jLhr9-vhtZjgUOqegbhxwgh2pNomHzHpJlpUTyPdbwlJOn9FBG70BJwhIuhU9aeGFqrt-fM4dY13FbS7KnApbVD8QsSUuue9hi47AEIjuEqY2FjT3wAG766x72E7HmkC9ffhjFZsddCEOif5P0kOP1pTHQYHDu5o44WWlovBuEPgJ3t8cB-kJRCjGxHRc1l8f866PteIU'
account_id = 'c6c1dc29-015a-4863-91aa-a4bf014c8dc9'


async def main():
    api = MetaApi(token)
    meta_stats = MetaStats(token)

    async def account_deploy():
        try:
            account = await api.metatrader_account_api.get_account(account_id)

            # wait until account is deployed and connected to broker
            print('Deploying account')

            if account.state != 'DEPLOYED':
                await account.deploy()
            else:
                print('Account already deployed')

            print('Waiting for API server to connect to broker (may take couple of minutes)')
        except Exception as err:
            print(api.format_error(err))

    await account_deploy()

    async def get_account_metrics():
        try:
            metrics = await meta_stats.get_metrics(account_id)
            print(metrics)  # -> {trades: ..., balance: ..., ...}
        except Exception as err:
            print(api.format_error(err))

    await get_account_metrics()

    async def get_account_trades(start_time: str, end_time: str):
        try:
            trades = await meta_stats.get_account_trades(account_id, start_time, end_time)
            print(trades[-5:])  # -> {_id: ..., gain: ..., ...}
        except Exception as err:
            print(api.format_error(err))

    await get_account_trades('2020-01-01 00:00:00.000', '2021-01-01 00:00:00.000')

    async def get_account_open_trades():
        try:
            open_trades = await meta_stats.get_account_open_trades(account_id)
            print(open_trades)  # -> {_id: ..., gain: ..., ...}
        except Exception as err:
            print(api.format_error(err))

    await get_account_open_trades()



# Run the main function in an asyncio event loop
asyncio.run(main())
