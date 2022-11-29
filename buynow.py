import ccxt
import json
import time

binance = ccxt.binance()
binance.load_markets()

trig_para = json.load(open('trig_para.json'))
interval = trig_para["interval"]
percent = trig_para["percent"]

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

                if item["diff_precent"] > percent:
                    item["buy_price"] = item["price"]
                    item["buy_time"] = item["time"]
                    catchPair.append(item)
        except Exception as e:
            print(e)
            pass

    for item in data:
        print(item)

    print("catch: ")
    for item in catchPair:
        print(item)
        print("keep time(s):", item["time"] - item["buy_time"], "profit:", (item["price"] - item["buy_price"])/item["buy_price"], "%")
    time.sleep(2)