import ccxt
import time
import json
from datetime import datetime
from decimal import Decimal
import random
import requests

secret = json.load(open('secret.json'))
exchange = ccxt.okx(secret["okx"])
exchange.load_markets()

# 可修改区域
symbol = "DORA-USDT-SWAP"
usdt_amount = 500
fundingRate = 0.003

# 币转张
def convert_sz(symbol, sz):
    url = "https://www.okx.com/api/v5/public/convert-contract-coin"
    order = exchange.fetch_order_book(symbol)
    px = order["bids"][0][0]
    print(symbol, "price:", px)
    unit = "usds"
    res = requests.get(url + "?" + "instId=" + symbol + "&" + "sz=" + str(sz) + "&" + "px=" + str(px) + "&" + "unit=" + str(unit))
    return res

# 合约张数
amount = convert_sz(symbol, usdt_amount).json()["data"][0]["sz"]
print("trade contract amount:", amount)

opening = False
buying = False
selling = False
frate = 0


print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "check time OK?")

# 测试买卖
#open = exchange.private_post_trade_order({"instId":symbol, "tdMode": "cross", "side": "buy", "posSide":"long", "ordType":"market", "sz": 1})
#print(open)
#close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "long"})
#print(close)

while True:
    try:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
        # 提前获取资费
        if (second > 30 and second < 50 and second % 5 == 0):
            frate = exchange.fetch_funding_rate(symbol)
            frate = frate["info"]["fundingRate"]
            #print(frate)

        if (not opening and abs(float(frate)) > fundingRate):
            if (hour == 0 and minute == 0 and (second >= 7 and second <= 9)) or \
                (hour == 8 and minute == 0 and (second >= 7 and second <= 9)) or \
                (hour == 16 and minute == 0 and (second >= 7 and second <= 9)):
                # 等 0.x 秒，随机值
                time.sleep(random.random())
                # 负资费买入
                if float(frate) < 0:
                    buying = True
                    open = exchange.private_post_trade_order({"instId":symbol, "tdMode": "cross", "side": "buy", "posSide":"long", "ordType":"market", "sz": amount})
                    print("buying:", open)
                # 正资费卖出
                if float(frate) > 0:
                    selling = True
                    open = exchange.private_post_trade_order({"instId":symbol, "tdMode": "cross", "side": "sell", "posSide":"short", "ordType":"market", "sz": amount})
                    print("selling:", open)
                opening = True
        if opening:
            if (hour == 0 and minute == 0 and (second >= 12 and second <= 15)) or \
                (hour == 8 and minute == 0 and (second >= 12 and second <= 15)) or \
                (hour == 16 and minute == 0 and (second >= 12 and second <= 15)):
                if buying:
                    buying = False
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "long"})
                    print(close, "closed")
                if selling:
                    selling = False
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "short"})
                    print(close, "closed")
                opening = False
                
        time.sleep(0.6)
    except Exception as e:
        print(type(e).__name__, str(e))
        pass
