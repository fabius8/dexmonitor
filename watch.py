import ccxt.pro
import numpy
import pandas
import talib
import time
from datetime import datetime
from asyncio import run, gather

print('CCXT Pro version', ccxt.pro.__version__)

MyTrader = {
    'balance': 100,
    'profit': 0,
    'number': 5,
    'opened': 0,
    'win_threshold': 0.1,
    'loss_threshold': 0.02,
    'timeperiod': 14,
    'n': 1,
    'p': 0.5,
    'k': 1,
    'ohlcv': {}
}

async def watch_order_book(exchange, symbol):
    while True:
        try:
            orderbook = await exchange.watch_order_book(symbol)
            datetime = exchange.iso8601(exchange.milliseconds())
            #print(datetime, orderbook['nonce'], symbol, orderbook['asks'][0], orderbook['bids'][0])
            print(MyTrader)
        except Exception as e:
            print(type(e).__name__, str(e))
            break

async def fetch_ohlcv(exchange, symbol, delay, n):
    if n > 50:
        return
    while True:
        try:
            await exchange.sleep(delay)
            timeframe = '15m'
            limit = 15
            # 当前k线也算
            since = exchange.milliseconds() - (limit) * exchange.parse_timeframe(timeframe) * 1000
            ohlcvs = await exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            data = numpy.array(ohlcvs)
            data = data.transpose()
            atr = talib.ATR(data[2], data[3], data[4], timeperiod=MyTrader["timeperiod"])
            #print("ATR:", atr[limit-1],(ohlcvs[limit-1][4] - ohlcvs[limit-1][1]), MyTrader["n"] * atr[limit-1], \
            #    (ohlcvs[limit-1][2] - ohlcvs[limit-1][4]), \
            #    ohlcvs[limit-1][5], MyTrader['k'] * numpy.mean(data[5]))
            # close - open > n * ATR
            # (high - close) < p * (high - low)
            # volume > k* avg(volume)
            #print(ohlcvs[limit-1])
            if (ohlcvs[limit-1][4] - ohlcvs[limit-1][1]) > MyTrader["n"] * atr[limit-1] and \
                (ohlcvs[limit-1][2] - ohlcvs[limit-1][4]) < MyTrader["p"] * (ohlcvs[limit-1][2] - ohlcvs[limit-1][3]) and \
                ohlcvs[limit-1][5] > MyTrader['k'] * numpy.mean(data[5]):
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ohlcvs[limit-1], "buy", symbol)
            #time.sleep(100)
            data = {"time": data[0], "open":data[1], "high":data[2], "low":data[3], "close":data[4], "volume":data[5]}
            data = pandas.DataFrame(data)
            data["time"] = data["time"].apply(lambda x: datetime.fromtimestamp(x/1000.0))
            now = exchange.milliseconds()
            #print(data)
            #print('\n===============================================================================')
            #print('Loop iteration:', 'current time:', exchange.iso8601(now), symbol, timeframe)
            #print('-------------------------------------------------------------------------------')
            #print(data)
        except Exception as e:
            #print(type(e).__name__, str(e), symbol)
            await exchange.sleep(10000)
            continue

async def main():
    exchange = ccxt.pro.binance()
    await exchange.load_markets()
    markets = list(exchange.markets.values())
    symbols = [market['symbol'] for market in markets if '/BUSD' in market['symbol']]
    print(symbols)
    #symbols = ['BTC/BUSD']
    delay = 2000  # 2s

    group1 = gather(*[fetch_ohlcv(exchange, symbol, delay, n) for n, symbol in enumerate(symbols)])
    #group2 = gather(*[watch_order_book(exchange, 'BTC/BUSD')])
    await gather(group1)
    await exchange.close()

run(main())