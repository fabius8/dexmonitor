import ccxt
import time
import json
from datetime import datetime
from decimal import Decimal
import random

secret = json.load(open('secret.json'))

exchange = ccxt.okx(secret["okx"])
exchange.load_markets()
symbol = "FITFI-USDT-SWAP"

opening = False
buying = False
selling = False
frate = 0
# 合约张数， 1张=10FITFI
amount = 223

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

        if (not opening and abs(float(frate)) > 0.01):
            if (hour == 0 and minute == 0 and (second >= 6 and second <= 8)) or \
                (hour == 8 and minute == 0 and (second >= 6 and second <= 8)) or \
                (hour == 16 and minute == 0 and (second >= 6 and second <= 8)):
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
            if (hour == 0 and minute == 0 and (second >= 17 and second <= 20)) or \
                (hour == 8 and minute == 0 and (second >= 17 and second <= 20)) or \
                (hour == 16 and minute == 0 and (second >= 17 and second <= 20)):
                if buying:
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "long"})
                    print(close, "closed")
                    buying = False
                if selling:
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "short"})
                    print(close, "closed")
                    selling = False
                opening = False
                
        time.sleep(0.6)
    except Exception as e:
        print(type(e).__name__, str(e))
        break
