import ccxt
import json
import time
from datetime import datetime, timezone, timedelta

binance = ccxt.binance()
binance.load_markets()

symbol = "BUSD/USDT"


while True:
    order_book = binance.fetch_order_book(symbol)
    print(order_book['bids'][0][0], order_book['asks'][0][0])
    time.sleep(60)


