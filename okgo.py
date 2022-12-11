import ccxt
import time
import json
import sys
from datetime import datetime
from decimal import Decimal
import random
import requests

secret = json.load(open('secret.json'))
exchange = ccxt.okx(secret["okx"])
exchange.load_markets()

# 可修改区域
symbol = "CELO-USDT-SWAP"
usdt_amount = 500
fundingRate = 0.003
open_second = 5
close_second = 20

if len(sys.argv) != 6:
    print("输入参数不对, python okgo.py <币对(BTC)-> <交易USD数量(如500)> <开始秒(如5)> <结束秒(如5)> <资费(如0.003)>")
    print("例子: python okgo.py BTC 500 5 15 0.003")
    sys.exit()
else:
    symbol = sys.argv[1] + "-USDT-SWAP"
    usdt_amount = sys.argv[2]
    open_second = int(sys.argv[3])
    close_second = int(sys.argv[4])
    if close_second < 10:
        print("close can't < 10")
        sys.exit()
    fundingRate = float(sys.argv[5])

print("币种: ", symbol)
print("交易数量: ", usdt_amount, "U")
print("开始: ", open_second, "秒")
print("结束: ", close_second, "秒")
print("资费: ", fundingRate, "")

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
print("合约张数: ", amount)

opening = False
buying = False
selling = False
frate = 0


print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "starting...")

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
            if (hour == 0 and minute == 0 and (second >= open_second and second <= 10)) or \
                (hour == 8 and minute == 0 and (second >= open_second and second <= 10)) or \
                (hour == 16 and minute == 0 and (second >= open_second and second <= 10)):
                # 等 0.x 秒，随机值
                #time.sleep(random.random())
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
            if (hour == 0 and minute == 0 and (second >= close_second and second <= 20)) or \
                (hour == 8 and minute == 0 and (second >= close_second and second <= 20)) or \
                (hour == 16 and minute == 0 and (second >= close_second and second <= 20)):
                if buying:
                    buying = False
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "long"})
                    print(close, "closed")
                if selling:
                    selling = False
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "short"})
                    print(close, "closed")
                opening = False
                print("close trading. exit!")
                break
                
        time.sleep(0.6)
    except Exception as e:
        print(type(e).__name__, str(e))
        pass
