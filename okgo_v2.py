import ccxt
import time
import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random
import requests

secret = json.load(open('secret.json'))
exchange = ccxt.okx(secret["okx"])
exchange.load_markets()

# 可修改区域
symbol = "LOOKS"
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
last_time = close_second - open_second
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

def get_left_seconds():
    now = datetime.now()
    base_time = datetime(2022, 12, 13, 0, 0, 0).replace(microsecond=0)
    diff = now - base_time
    seconds = diff.total_seconds()
    left_seconds = 1 - (int(seconds * 1000000) / int(3600 * 8 * 1000000) - int(seconds * 1000000) // int(3600 * 8 * 1000000))
    next_time = now + timedelta(seconds = left_seconds * 3600 * 8)
    print("距离下次资费结算时间", next_time,"还剩下:", int(left_seconds * 3600 * 8), "秒", end = '\r')
    return left_seconds * 3600 * 8


frate = exchange.fetch_funding_rate(symbol)
frate = float(frate["info"]["fundingRate"])
print("现在资费:", frate)
while True:
    try:
        buy = False
        sell = False
        if get_left_seconds() <= 1:
            # 开始 x 秒
            time.sleep(open_second)
            order = exchange.fetch_order_book(symbol)
            bid = order["bids"][0][0]
            ask = order["asks"][0][0]
            #print(type(ask))
            ################## 买入
            if frate < 0:
                buy_price = ask * (1 - abs(frate)/2)
                print("买入价格:", buy_price)
                tpTriggerPx = ask
                print("止盈价格:", tpTriggerPx)
                open = exchange.private_post_trade_order({ \
                        "instId":symbol, \
                        "tdMode": "cross", \
                        "side": "buy", \
                        "posSide": "long", \
                        "ordType": "limit", \
                        "px": buy_price, \
                        "tpTriggerPx": tpTriggerPx, \
                        "tpOrdPx": -1, \
                        "sz": amount \
                    })
                orderID = open["data"][0]["ordId"]
                print("委托下单编号:", orderID)

                # 结束时间第5秒
                time.sleep(5 - open_second)
                try:
                    cancel_order = exchange.private_post_trade_cancel_order({"instId": symbol, "ordId": orderID})
                    print("撤销订单成功", cancel_order)
                except Exception as e:
                    print("撤销订单失败", type(e).__name__, str(e))
                    pass

                # 结束时间第15秒
                time.sleep(close_second - 5)
                try:
                    algoId = exchange.private_get_trade_orders_algo_pending({"ordType":"conditional"})
                    #print(algoId)
                    for i in algoId["data"]:
                        algoId = i["algoId"]
                        print(algoId)
                        cancel_algos = exchange.private_post_trade_cancel_algos([{"algoId":algoId, "instId": symbol}])
                        print("止盈策略撤销成功", cancel_algos)
                except Exception as e:
                    print("止盈策略撤销失败", type(e).__name__, str(e))
                    pass
                try:
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "long"})
                    print("平仓", close)
                except Exception as e:
                    print("仓位不存在", type(e).__name__, str(e))
                    break 
                break
            ################## 卖出
            if frate > 0:
                sell_price = bid * (1 + abs(frate)/2)
                print("卖出价格:", sell_price)
                tpTriggerPx = bid
                print("止盈价格:", tpTriggerPx)
                open = exchange.private_post_trade_order({ \
                        "instId":symbol, \
                        "tdMode": "cross", \
                        "side": "sell", \
                        "posSide": "short", \
                        "ordType": "limit", \
                        "px": sell_price, \
                        "tpTriggerPx": tpTriggerPx, \
                        "tpOrdPx": -1, \
                        "sz": amount \
                    })
                orderID = open["data"][0]["ordId"]
                print("委托下单编号:", orderID)

                # 结束时间第5秒
                time.sleep(5 - open_second)
                try:
                    cancel_order = exchange.private_post_trade_cancel_order({"instId": symbol, "ordId": orderID})
                    print("撤销订单成功", cancel_order)
                except Exception as e:
                    print("撤销订单失败", type(e).__name__, str(e))
                    pass
                # 结束时间第15秒
                time.sleep(close_second - 5)
                try:
                    algoId = exchange.private_get_trade_orders_algo_pending({"ordType":"conditional"})
                    #print(algoId)
                    for i in algoId["data"]:
                        algoId = i["algoId"]
                        print(algoId)
                        cancel_algos = exchange.private_post_trade_cancel_algos([{"algoId":algoId, "instId": symbol}])
                    print("止盈策略撤销成功", cancel_algos)
                except Exception as e:
                    print("止盈策略撤销失败", type(e).__name__, str(e))
                    pass
                try:
                    close = exchange.private_post_trade_close_position({"instId":symbol, "mgnMode":"cross", "posSide": "short"})
                    print("平仓", close)
                except Exception as e:
                    print("仓位不存在", type(e).__name__, str(e))
                    break
                break
        time.sleep(1)
    except Exception as e:
        print(type(e).__name__, str(e))
        break