import ccxt.pro
import asyncio
import json
from pprint import pprint

async def watch_loop(exchange, symbol, n):
    #  timestamp, open, high, low, close, volume
    timeframe = '1m'
    limit = 2
    burst = 0.01*10000
    while True:
        try:
            ohlcvs = await exchange.watch_ohlcv(symbol, timeframe, None, limit)
            open = ohlcvs[0][1]
            high = ohlcvs[0][2]
            low  = ohlcvs[0][3]
            close= ohlcvs[0][4]
            cur_diff = int((close - open)/open*10000)
            max_diff = int((high - low)/open*10000)
            if (abs(cur_diff) > burst):
                print('{0:>16}'.format(symbol), '{0:>8.2%}'.format(cur_diff/10000), "::", exchange.iso8601(ohlcvs[0][0]), "price:", close)
        except Exception as e:
            #print(type(e).__name__, str(e))
            continue
            

async def main(exchange):
    await exchange.load_markets()
    markets = list(exchange.markets.values())
    symbols = [market['symbol'] for market in markets if '/BUSD' in market['symbol']]
    await asyncio.gather(*[watch_loop(exchange, symbol, n) for n, symbol in enumerate(symbols)])
    await exchange.close()

exchange = ccxt.pro.binance()
asyncio.run(main(exchange))