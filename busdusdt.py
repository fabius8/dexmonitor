import ccxt
import json
import time
from datetime import datetime, timezone, timedelta

secret = json.load(open('secret.json'))
binance = ccxt.binance(secret["binance"])
binance.load_markets()

symbol = "BUSD/USDT"
per_amount = 20000

while True:
    order_book = binance.fetch_order_book(symbol)
    bid = order_book['bids'][0][0]
    ask = order_book['asks'][0][0]
    balance = binance.fetchBalance()
    for asset in balance["info"]["balances"]:
        #sell busd
        if asset['asset'] == "BUSD" and float(asset['free']) > 10.0:
            if float(asset['free']) > per_amount:
                sell = binance.createLimitSellOrder(symbol, per_amount, ask)
            else:
                sell = binance.createLimitSellOrder(symbol, int(float(asset['free'])), ask)
            print(sell)
        #buy busd
        if asset['asset'] == "USDT" and float(asset['free']) > 10.0:
            if float(asset['free']) > per_amount:
                buy = binance.createLimitBuyOrder(symbol, per_amount, bid)
            else:
                buy = binance.createLimitBuyOrder(symbol, int(float(asset['free'])), bid)
            print(buy)
    time.sleep(10)


