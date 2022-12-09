import ccxt
import json


exchange = ccxt.binance()
exchange.load_markets()

order_book = exchange.fetch_order_book("BUSD/USDT")
print(order_book)

bid0_p = order_book['bids'][0][0]
bid0_v = order_book['bids'][0][1]
ask0_p = order_book['asks'][0][0]
ask0_v = order_book['asks'][0][1]
# 买一 卖一 委托单价格、委托量
bid1_p = order_book['bids'][1][0]
ask1_p = order_book['asks'][1][0]

print(bid0_p, bid0_v, ask0_p, ask0_v, bid1_p, ask1_p)