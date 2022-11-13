from uniswap import Uniswap
import ccxt
import logging
import time

address = None         # or None if you're not going to make transactions
private_key = None  # or None if you're not going to make transactions
version = 2                       # specify which version of Uniswap to use
provider = "https://bsc-dataseed.binance.org/"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
binance = ccxt.binance()
binance.load_markets()

logging.basicConfig(level=logging.ERROR)

# Some token addresses we'll be using later in this guide
ETH = "0x0000000000000000000000000000000000000000"
BNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
BUSD = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
LUNA = "0x156ab3346823B651294766e23e6Cf87254d68962"
USDT = "0x55d398326f99059fF775485246999027B3197955"
YFII = "0x7F70642d88cf1C4a3a7abb072B53B929b653edA5"

while True:
    time.sleep(5)
    SYMBOL = "BNB"
    order_book = binance.fetch_order_book(SYMBOL + "/USDT")
    bid = order_book['bids'][0][0]
    price = uniswap.get_price_input(BNB, USDT, 10**18)
    print("BNB:", BNB)
    print("pancake price ", ":", price/10**18)
    print("binance price ", ":", bid)
    print("------")


