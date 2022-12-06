import ccxt
import ccxt.pro
import json
from asyncio import run, gather
import time
from datetime import datetime
import sys

"""
secret = json.load(open('secret.json'))
binance = ccxt.binance(secret["binance"])
binance.load_markets()
symbols = []
data = binance.sapi_get_loan_loanable_data()
for row in data["rows"]:
    symbol = row["loanCoin"] + "/USDT"
    if symbol in binance.markets:
        symbols.append(symbol)
        continue
    symbol = row["loanCoin"] + "/BUSD"
    if symbol in binance.markets:
        symbols.append(symbol)
"""

async def watch_loop(spot, future, symbol, n):
    #  timestamp, open, high, low, close, volume        
    timeframe = '1m'
    limit = 2
    diff = 0.001*100
    while True:
        try:
            await time.sleep(5)
            print("here")
            ohlcvs_future = await future.watch_ohlcv(symbol, timeframe, None, limit)
            ohlcvs_spot = await spot.watch_ohlcv(symbol, timeframe, None, limit)
            open_future = ohlcvs_future[0][1]
            high_future = ohlcvs_future[0][2]
            low_future  = ohlcvs_future[0][3]
            close_future = ohlcvs_future[0][4]

            open_spot = ohlcvs_spot[0][1]
            high_spot = ohlcvs_spot[0][2]
            low_spot  = ohlcvs_spot[0][3]
            close_spot = ohlcvs_spot[0][4]
            cur_diff = int((close_spot - close_future)/close_future*100)
            

            if (cur_diff > diff):
                print('{0:>16}'.format(symbol), '{0:>8.2%}'.format(cur_diff/100), "::", ohlcvs_spot.iso8601(open_spot[0][0]), "price:", close_spot)
                print('{0:>16}'.format(symbol), '{0:>8.2%}'.format(cur_diff/100), "::", ohlcvs_future.iso8601(open_future[0][0]), "price:", close_future)
                #loan = binance.sapi_post_margin_loan({"asset":symbol[:-5], "amount":0.001})
                print("loan create")
                break
                
        except Exception as e:
            print(type(e).__name__, str(e), symbol)
            pass

async def main():
    try:
        binance_spot = ccxt.pro.binance({'options':{'defaultType':'spot'}})
        markets_spot = await binance_spot.load_markets()
        binance_future = ccxt.pro.binance({'options':{'defaultType':'future'}})
        markets_future = await binance_future.load_markets()
        pair_usdt = []
        pair_busd = []
        pair_fix = []
        pair_all = []
        for i in markets_future:
            if "/USDT" in i:
                pair_usdt.append(i[:-5])
                continue
            if "/BUSD" in i:
                pair_busd.append(i[:-5])
        print(pair_usdt, len(pair_usdt))
        print(pair_busd, len(pair_busd))
        for i in pair_busd:
            if i not in pair_usdt:
                pair_fix.append(i)
        for i in pair_fix:
            i = i + '/BUSD'
            pair_all.append(i)
        for i in pair_usdt:
            i = i + '/USDT'
            pair_all.append(i)
        print(pair_all, len(pair_all))
        await gather(*[watch_loop(binance_spot, binance_future, symbol, n) for n, symbol in enumerate(pair_all)])
        await binance_spot.close()
        await binance_future.close()
    except Exception as e:
        print(type(e).__name__, str(e))
        pass


run(main())
