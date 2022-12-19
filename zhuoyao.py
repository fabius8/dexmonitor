import ccxt
from apscheduler.schedulers.blocking import BlockingScheduler
import time
from datetime import datetime
import random
import logging
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.ERROR)
exchange = ccxt.binance()
exchange.load_markets()
symbols = [] 


def init():
    for symbol in exchange.markets:
        if "/USDT" in symbol:
            try:
                if len(symbols) > 500:
                    break
                order_book = exchange.fetch_order_book(symbol)
                order_book["bids"][0][0]
                symbols.append(symbol)
                print(symbol)
            except Exception as e:
                #print(e)
                pass

init()
print("监控", len(symbols), "个币", symbols)

def monitor(symbol):
    time.sleep(random.randint(1, 100))
    timeframe = '3m'
    s = symbol.replace("/", "")
    limit = 1
    diff = 0
    try:
        ohlcv = exchange.public_get_klines({"symbol": s, "interval":timeframe, "limit": limit})
        open = float(ohlcv[0][1])
        close = float(ohlcv[0][4])
        cur = (close - open) / open
        if abs(cur) >= diff:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '{0:>8}'.format(str(symbols.index(symbol)) + "/" + str(len(symbols))) + " " + '{0:>10}'.format(symbol), "价格波动超过", "{0:>8.2%}".format(cur))
    except Exception as e:
        print(type(e).__name__, str(e), symbol)
        pass

sched = BlockingScheduler()

for symbol in symbols:
    sched.add_job(monitor, args=[symbol,], trigger='interval', seconds=100, next_run_time=datetime.now())

sched.start()

