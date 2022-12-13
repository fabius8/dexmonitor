import ccxt.pro
import asyncio
import json
from pprint import pprint
from datetime import datetime
import time

async def watch_loop(exchange, symbol, n):
    #  timestamp, open, high, low, close, volume
    if n > 20:
        return
    timeframe = '1m'
    limit = 2
    burst = 0.01*10000

    try:
        #await asyncio.sleep(1)
        await exchange.throttle(1)
        order = await exchange.watch_order_book(symbol)
        #ohlcvs = await exchange.watch_ohlcv(symbol, timeframe, None, limit)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, order["bids"][0][0])

    except Exception as e:
        print(type(e).__name__, str(e), symbol)
        pass
        
            

async def main(exchange):
    await exchange.load_markets()
    markets = list(exchange.markets.values())
    symbols = [market['symbol'] for market in markets if '/BUSD' in market['symbol']]
    print(symbols)
    while True:
        await asyncio.gather(*[watch_loop(exchange, symbol, n) for n, symbol in enumerate(symbols)])
        print("haha")
        time.sleep(2)
        #await asyncio.sleep(1)
    #await exchange.close()

exchange = ccxt.pro.binance()
asyncio.run(main(exchange))