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
version = 3                       # specify which version of Uniswap to use
provider = "https://rpc.ankr.com/eth"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
print("init...")

ETH = "0x0000000000000000000000000000000000000000"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
MONEY = 1

logging.basicConfig(level=logging.ERROR)
tokens = json.load(open('uniswap.json'))

errCount = 0

try:
    coinbase = ccxt.coinbase()
    coinbase.load_markets()
except Exception as e:
    pass

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

while True:
    count = 1
    try:
        data = coinbase.publicGetPricesSymbolSpot({"symbol": "ETH-USD"})
        eth_price = float(data["data"]["amount"])
        if errCount > 5:
            print("error too many, sleep...")
            time.sleep(120)
            uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
            coinbase = ccxt.coinbase()
            coinbase.load_markets()
            errCount = 0

        for token in tokens:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, "/", len(tokens), token["symbol"], token["contract"])

            buyAmount = uniswap.get_price_input(WETH, Web3.toChecksumAddress(token["contract"]), MONEY * 10**18, token["fee"])
            buyAmount = buyAmount / 10**token["decimals"]
            buyPrice =  eth_price * MONEY / buyAmount

            sellAmount = uniswap.get_price_output(Web3.toChecksumAddress(token["contract"]), WETH, MONEY * 10**18, token["fee"])
            sellAmount = sellAmount / 10**token["decimals"]
            sellPrice =  eth_price * MONEY / sellAmount

            symbol = token["symbol"] + "-USD"
            data = coinbase.publicGetPricesSymbolSpot({"symbol": symbol})
            cbprice = float(data["data"]["amount"])

            print("Uniswap B price:", buyPrice, "Amount:", buyAmount)
            print("Uniswap S price:", sellPrice, "Amount", sellAmount)
            print("Coinbase  price:", cbprice)
            buy_diff = 100 * ((cbprice - buyPrice)/buyPrice)
            sell_diff = 100 * ((sellPrice - cbprice)/cbprice)
            print("B diff:", "%.2f" %buy_diff, "%")
            print("S diff:", "%.2f" %sell_diff, "%")

            if buy_diff > 2:
                text = "品种:" + token["symbol"] + "\n"
                text += "合约:" + token["contract"] + "\n"
                text += "时间:" + datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") + "\n"
                text += "Coinbase价格:" + str(cbprice) + "\n"
                text += "Uniswap价格:" + str(buyPrice) + "\n"
                text += "可交易数量:" +  str(buyAmount) + "\n"
                text += "价差:" + format(buy_diff, ".2f") + "%" + "\n"
                sendmsg(text)
                print("send msg")
                beep()
            print(" ")
            if sell_diff > 2:
                text = "品种:" + token["symbol"] + "\n"
                text += "合约:" + token["contract"] + "\n"
                text += "时间:" + datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") + "\n"
                text += "Coinbase价格:" + str(cbprice) + "\n"
                text += "Uniswap价格:" + str(sellPrice) + "\n"
                text += "可交易数量:" + str(sellAmount) + "\n"
                text += "价差:" + format(sell_diff, ".2f") + "%" +  "\n"
                sendmsg(text)
                print("send msg")
                beep()
            print("")
            count = count + 1
        print("------")
    except Exception as e:
        print(e)
        errCount = errCount + 1
        pass
    time.sleep(5)
