import ccxt
import json
import time

binance = ccxt.binance()
binance.load_markets()

trig_para = json.load(open('trig_para.json'))
interval = trig_para["interval"]
percent = trig_para["percent"]

busdPair = []
data = []
catchPair = []

print("init...")
for symbol in binance.markets:
    if "/BUSD" in symbol:
        try:
            order_book = binance.fetch_order_book(symbol)
            first_price = order_book['bids'][0][0]
            item = {"symbol": symbol, "previous_price": first_price, "previous_time": int(time.time()), "price": None, "time": None, "direct": None, "diff_interval": None, "diff_precent": None}
            data.append(item)
        except Exception as e:
            pass

while True:
    for item in data:
        try:
            order_book = binance.fetch_order_book(item["symbol"])
            price = order_book['bids'][0][0]
            item["price"] = price
            item["time"] = int(time.time())
            if (item["time"] - item["previous_time"]) > interval:
                item["diff_interval"] = int(item["time"] - item["previous_time"])
                item["diff_precent"] = 100 * (item["price"] - item["previous_price"])/item["previous_price"]
                item["previous_time"] = item["time"]
                if item["price"] > item["previous_price"]:
                    item["direct"] = "📈UP"
                elif item["price"] < item["previous_price"]:
                    item["direct"] = "📉DOWN"
                item["previous_price"] = item["price"]
            if float(item["diff_precent"]) > percent:
                catchPair.append[item]
        except Exception as e:
            print(e)
            pass

    for item in data:
        print(item)

    print("catch: ", catchPair)
    time.sleep(2)