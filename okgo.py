import ccxt
import time
import json
from datetime import datetime
from decimal import Decimal

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

while True:
    try:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
        # 提前获取资费
        if (second > 30 and second < 50 and second % 2 == 0):
            frate = exchange.fetch_funding_rate(symbol)
            frate = frate["info"]["fundingRate"]
        #print(frate)

        if (not opening and abs(float(frate)) > 0.01):
            if (hour == 0 and minute == 0 and (second >= 6 and second <= 8)) or \
                (hour == 8 and minute == 0 and (second >= 6 and second <= 8)) or \
                (hour == 16 and minute == 0 and (second >= 6 and second <= 8)):
                # 负资费买入
                if float(frate) < 0:
                    open = exchange.private_post_trade_order({"instId":symbol, "tdMode": "cross", "side": "buy", "posSide":"long", "ordType":"market", "sz": amount})
                    buying = True
                    print("buying:", open)
                # 正资费卖出
                if float(frate) > 0:
                    open = exchange.private_post_trade_order({"instId":symbol, "tdMode": "cross", "side": "sell", "posSide":"short", "ordType":"market", "sz": amount})
                    selling = True
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
                
        time.sleep(0.5)
    except Exception as e:
        print(type(e).__name__, str(e))
        break
