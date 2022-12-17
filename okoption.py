import ccxt
import time
from datetime import datetime
import sys

exchange = ccxt.okx()
exchange.load_markets()

symbol = "BTC"

filter = "17000-P"

if len(sys.argv) != 2:
    print("输入参数不对")
    print("例子: python okoption.py 17000-P")
    sys.exit()

filter = sys.argv[1]

def get_profit_by_day(filter):
    order = exchange.fetch_order_book(symbol + "-USDT")
    price = order["bids"][0][0]
    print(symbol, "price:", price)

    data = exchange.public_get_public_instruments({"instType": "OPTION", "uly": symbol + "-USD"})["data"]
    for i in data:
        instId = i["instId"]
        info = exchange.public_get_market_ticker({"instId": instId})
        if filter in info["data"][0]["instId"]:
            eT = info["data"][0]["instId"][8:14]
            eTime = "20" + eT[0:2] + "/" + eT[2:4] + "/" + eT[4:6] + " " + "16:00:00"
            T1 = datetime.strptime(eTime, "%Y/%m/%d %H:%M:%S")
            T2 = int(datetime.timestamp(T1))
            ts = int(info["data"][0]["ts"])/1000
            diff = T2 - ts
            left_day = float(diff) / (3600*24)
            bid =  price * float(info["data"][0]["bidPx"]) if info["data"][0]["bidPx"] != "" else 0
            day_profit = bid / left_day
            print(info["data"][0]["instId"], "price: ", int(bid), ", day profit", int(day_profit))


get_profit_by_day(filter)

#data = exchange.public_get_public_instruments({"instType": "OPTION", "uly": symbol + "-USD"})["data"]
#for i in data:
#    get_profit_by_day(i["instId"][8:14])