import ccxt
import json
import time
from copy import deepcopy
from datetime import datetime, timezone, timedelta


binance = ccxt.binance()
binance.load_markets()

trig_para = json.load(open('trig_para.json'))
interval = trig_para["interval"]
percent = trig_para["percent"]
loss_percent = trig_para["loss_percent"]

money = 1000000
data = []
catchPair = []

print("init...")
for symbol in binance.markets:
    if "/BUSD" in symbol:
        try:
            order_book = binance.fetch_order_book(symbol)
            first_price = order_book['bids'][0][0]
            item = {
                "symbol": symbol, 
                "previous_price": first_price, 
                "previous_time": int(time.time()), 
                "price": first_price, 
                "time": int(time.time()), 
                "direct": None, 
                "diff_interval": None, 
                "diff_precent": None,
                "buy_price": None,
                "buy_time": None}
            data.append(item)
        except Exception as e:
            #print(e)
            pass

while True:
    for item in data:
        try:
            order_book = binance.fetch_order_book(item["symbol"])
            price = order_book['bids'][0][0]
            if (int(time.time()) - item["previous_time"]) > interval:
                item["previous_time"] = item["time"]
                item["previous_price"] = item["price"]
                item["time"] = int(time.time())
                item["price"] = price
                item["diff_interval"] = item["time"] - item["previous_time"]
                item["diff_precent"] = float(format(100 * (item["price"] - item["previous_price"])/item["previous_price"], ".2f"))
                
                if item["price"] > item["previous_price"]:
                    item["direct"] = "📈UP"
                elif item["price"] < item["previous_price"]:
                    item["direct"] = "📉DOWN"
                #print(item)
                if item["diff_precent"] > percent:
                    if item not in catchPair:
                        item["buy_price"] = item["price"]
                        item["buy_time"] = item["time"]
                        print("buy")
                        print(item)
                        catchPair.append(item)

                for citem in catchPair:
                    if 100*(citem["price"] - citem["buy_price"])/citem["buy_price"] < loss_percent or (citem["time"] - citem["buy_time"]) > 60:
                        money = money * (1 + (citem["price"] - citem["buy_price"])/citem["buy_price"])
                        print("sell")
                        print(citem)
                        print("keep time(s):", citem["time"] - citem["buy_time"], "profit:", format(100*(citem["price"] - citem["buy_price"])/citem["buy_price"], ".2f"), "%")
                        catchPair.remove(citem)
                        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Money: ", money)

        except Exception as e:
            print(e)
            pass
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Money: ", money)
    time.sleep(2)