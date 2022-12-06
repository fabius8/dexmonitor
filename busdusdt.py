import ccxt
import json
import time
from datetime import datetime, timezone, timedelta

secret = json.load(open('secret.json'))
binance = ccxt.binance(secret["binance"])
binance.load_markets()

symbol = "BUSD/USDT"
per_amount = 20000
errCount = 0


while True:
    try:
        if errCount > 5:
            binance = ccxt.binance(secret["binance"])
            binance.load_markets()
            time.sleep(120)
            errCount = 0

        totalU = 0
        order_book = binance.fetch_order_book(symbol)
        bid = order_book['bids'][0][0]
        ask = order_book['asks'][0][0]
        balance = binance.fetchBalance()
    
        for asset in balance["info"]["balances"]:
            if asset['asset'] == "USDT":
                totalU = totalU + float(asset["free"]) + float(asset["locked"])
            elif asset['asset'] == "BUSD":
                totalU = totalU + (float(asset["free"]) + float(asset["locked"])) * bid

        for asset in balance["info"]["balances"]:
            #sell busd
            if asset['asset'] == "BUSD" and float(asset['free']) > 1000.0:
                if float(asset['free']) > per_amount:
                    sell = binance.createLimitSellOrder(symbol, per_amount, ask)
                else:
                    sell = binance.createLimitSellOrder(symbol, int(float(asset['free'])), ask)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sell["info"])
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Total USD:", totalU)
                
            #buy busd
            if asset['asset'] == "USDT" and float(asset['free']) > 1000.0:
                if float(asset['free']) > per_amount:
                    buy = binance.createLimitBuyOrder(symbol, per_amount, bid)
                else:
                    buy = binance.createLimitBuyOrder(symbol, int(float(asset['free'])), bid)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), buy["info"])
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Total USD:", totalU)
            
        openOrders = binance.fetchOpenOrders(symbol=symbol)
        #cancel outdate orders
        for openOrder in openOrders:
            if openOrder["info"]["side"] == "BUY" and float(openOrder["info"]["price"]) < bid:
                cancelOrder = binance.cancel_order(openOrder["info"]["orderId"], openOrder["info"]["symbol"])
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cancelOrder["info"])
            if openOrder["info"]["side"] == "SELL" and float(openOrder["info"]["price"]) > ask:
                cancelOrder = binance.cancel_order(openOrder["info"]["orderId"], openOrder["info"]["symbol"])
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cancelOrder["info"])
    except Exception as e:
        print(e)
        errCount = errCount + 1
        pass
    time.sleep(5)


