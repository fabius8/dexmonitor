from uniswap import Uniswap
import ccxt
import logging
import time
import json

address = None         # or None if you're not going to make transactions
private_key = None  # or None if you're not going to make transactions
version = 2                       # specify which version of Uniswap to use
provider = "https://bsc-dataseed.binance.org/"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
binance = ccxt.binance()
binance.load_markets()

logging.basicConfig(level=logging.ERROR)
tokens = json.load(open('token.json'))
print(tokens)

BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
USDT = "0x55d398326f99059fF775485246999027B3197955"

BASE = "USDT"

while True:
    time.sleep(5)
    for token in tokens:
        order_book = binance.fetch_order_book(token["symbol"] + "/" + BASE)
        bid = order_book['bids'][0][0]
        price = uniswap.get_price_input(token["contract"], USDT, 10**18)
        print(token["symbol"], ":", token["contract"])
        print("pancake price ", ":", price/10**18)
        print("binance price ", ":", bid)
        print("------")


