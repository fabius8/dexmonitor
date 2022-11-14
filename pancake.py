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

while True:
    try:
        for token in tokens:
            #print("route :", token["route"])
            price = uniswap.get_price_input(
                Web3.toChecksumAddress(token["contract"]), 
                USDT, 
                10**token["decimals"],
                None,
                token["route"])
            print(token["symbol"], ":", token["contract"])

            try:
                order_book = binance.fetch_order_book(token["symbol"] + "/" + BASE)
            except Exception as e:
                print(e)
                pass
                continue
            bid = order_book['bids'][0][0]

            print("pancake price ", ":", price/(10**18))
            print("binance price ", ":", bid)
            diff = 100 * ((price/(10**18) - bid)/bid)
            print("diff", ":",  "%.2f" %diff, "%")
            if abs(diff) > 2:
                print("😱 diff is big!")
            print(" ")
        print("------")
    except Exception as e:
        print(e)
        pass
    time.sleep(5)

