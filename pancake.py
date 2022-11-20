from uniswap import Uniswap
from web3 import Web3
import ccxt
import logging
import time

import json
import requests
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=+8))
address = None         # or None if you're not going to make transactions
private_key = None  # or None if you're not going to make transactions
version = 2                       # specify which version of Uniswap to use
provider = "https://bsc-dataseed.binance.org/"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
print("init...")


logging.basicConfig(level=logging.ERROR)
tokens = json.load(open('token.json'))

BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
USDT = "0x55d398326f99059fF775485246999027B3197955"
ETH = "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
BASE = "USDT"

def beep():
    print("\a")

alert = None
try:
    alert = json.load(open('alert.json'))
except Exception as e:
    pass


def sendmsg(text):
    if alert is None:
        return
    params = {
        "corpid": alert['corpid'],
        "corpsecret": alert['corpsecret']
    }
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    r = requests.get(url, params = params)
    access_token = r.json()["access_token"]
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
    params = {
        "access_token": access_token
    }
    data = {
        "touser": "@all",
        "msgtype" : "text",
        "agentid" : alert['agentid'],
        "text" : {
            "content" : text
        }
    }
    r = requests.post(url, params = params, json = data)


try:
    binance = ccxt.binance()
    binance.load_markets()
except Exception as e:
    pass

errCount = 0

while True:
    count = 1

    try:
        if errCount > 5:
            uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
            errCount = 0
        
        for token in tokens:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, "/", len(tokens), token["symbol"], token["contract"])
            # buy mode
            buyAmount = uniswap.get_price_input(BUSD, Web3.toChecksumAddress(token["contract"]), 100 * 10**18, None, token["buyRoute"])
            buyAmount = buyAmount / 10**token["decimals"]
            buyPrice = 100 / buyAmount

            # sell mode
            sellAmount = uniswap.get_price_output(Web3.toChecksumAddress(token["contract"]), BUSD, 100 * 10**18, None, token["sellRoute"])
            sellAmount = sellAmount / 10**token["decimals"]
            sellPrice = 100 / sellAmount
            try:
                if token["symbol"] == "PROS":
                    order_book = binance.fetch_order_book(token["symbol"] + "/" + "BUSD")
                else:
                    order_book = binance.fetch_order_book(token["symbol"] + "/" + BASE)
            except Exception as e:
                print(e)
                pass
                continue
            bid = order_book['bids'][0][0]

            print("pancake B price ", ":", buyPrice, "Amount:", buyAmount)
            print("pancake S price ", ":", sellPrice, "Amount", sellAmount)
            print("binance price ", ":", bid)
            buy_diff = 100 * ((bid - buyPrice)/buyPrice)
            sell_diff = 100 * ((sellPrice - bid)/bid)
            print("B diff", ":",  "%.2f" %buy_diff, "%")
            print("S diff", ":",  "%.2f" %sell_diff, "%")
            


            if buy_diff > 1.2:
                text = token["symbol"] + " " + token["contract"] + "\n"
                text += datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") + "\n"
                text += "binance price " + ": " + str(bid) + "\n"
                print("😱 profit is big! Pancake -> Binance ")
                text += "pancake B price" + ": " + str(buyPrice) + " Amount: " +  str(buyAmount) + "\n"
                text += "😱 profit is big! Pancake -> Binance" + " diff: " + format(buy_diff, ".2f") + "%" + "\n"
                sendmsg(text)
                beep()
            print(" ")
            if sell_diff > 1.2:
                text = token["symbol"] + " " + token["contract"] + "\n"
                text += datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") + "\n"
                text += "binance price " + ": " + str(bid) + "\n"
                print("😱 profit is big! Binance -> Pancake ")
                text += "pancake S price" + ": " + str(sellPrice) + " Amount: " + str(sellAmount) + "\n"
                text += "😱 profit is big! Binance -> Pancake"  + " diff: " + format(sell_diff, ".2f") + "%" +  "\n"
                sendmsg(text)
                beep()
            print(" ")
            count = count + 1
        print("------")
    except Exception as e:
        print(e)
        errCount = errCount + 1
        time.sleep(120)
        pass
    time.sleep(5)

