import ccxt
import schedule
import time
from datetime import datetime

symbol = "APE-USDT-SWAP"
exchange = ccxt.okx({"options":{"defaultType": "future"}})

def getprice():
    order = exchange.fetch_order_book(symbol)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "bid:", order["bids"][0][0], "ask:", order["asks"][0][0])


schedule.every().second.do(lambda: getprice())
while True:
    schedule.run_pending()
    time.sleep(1)