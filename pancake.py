from uniswap import Uniswap
from web3 import Web3
import ccxt
import logging
import time
import json

address = None         # or None if you're not going to make transactions
private_key = None  # or None if you're not going to make transactions
version = 2                       # specify which version of Uniswap to use
provider = "https://bsc-dataseed.binance.org/"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
print("init...")
binance = ccxt.binance()
binance.load_markets()

logging.basicConfig(level=logging.ERROR)
tokens = json.load(open('token.json'))

BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
USDT = "0x55d398326f99059fF775485246999027B3197955"
ETH = "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
BASE = "USDT"

exPrice = {}

def initPrice():
    global exPrice
    for token in tokens:
        order_book = binance.fetch_order_book(token["symbol"] + "/" + BASE)
        bid = order_book['bids'][0][0]
        exPrice[token["symbol"]] = bid

initPrice()
print(exPrice)

def beep():
    print("\a")

while True:
    try:
        for token in tokens:
            #print("route :", token["route"])
            # buy mode
            buyAmount = 100 / exPrice[token["symbol"]]
            if buyAmount < 1:
                buyAmount = 1
            else:
                buyAmount = int(buyAmount)
            buyPrice = uniswap.get_price_input( Web3.toChecksumAddress(token["contract"]), BUSD, buyAmount * 10**token["decimals"], None, token["buyRoute"])
            print(token["symbol"], ":", token["contract"])
            buyPrice = buyPrice / buyAmount
            buyPrice = buyPrice / (10**18)
            # sell mode
            sellAmount = uniswap.get_price_output(Web3.toChecksumAddress(token["contract"]), BUSD, 100 * 10**18, None, token["buyRoute"])
            sellAmount = sellAmount / 10**token["decimals"]
            sellPrice = 100 / sellAmount
            try:
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

            if buy_diff > 2:
                print("😱 profit is big! Pancake -> Binance")
                beep()
            if sell_diff > 2:
                print("😱 profit is big! Binance -> Pancake")
                beep()
            print(" ")
        print("------")
    except Exception as e:
        print(e)
        pass
    time.sleep(5)

