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
provider = "https://eth-mainnet.public.blastapi.io"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
print("init...")

ETH = "0x0000000000000000000000000000000000000000"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
MONEY = 500

logging.basicConfig(level=logging.ERROR)
tokens = json.load(open('uniswap.json'))

errCount = 0

try:
    coinbase = ccxt.coinbase()
    coinbase.load_markets()
except Exception as e:
    pass
data = coinbase.publicGetPricesSymbolSpot({"symbol": "ETH-USD"})
eth_price = data["data"]["amount"]

while True:
    count = 1
    try:
        if errCount > 5:
            uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
            errCount = 0

        for token in tokens:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, "/", len(tokens), token["symbol"], token["contract"])

            try:
                buyAmount = uniswap.get_price_input(USDT, Web3.toChecksumAddress(token["contract"]), MONEY * 10**6, token["fee"])
                buyAmount = buyAmount / 10**token["decimals"]
                buyPrice =  MONEY / buyAmount

                sellAmount = uniswap.get_price_output(Web3.toChecksumAddress(token["contract"]), USDT, MONEY * 10**6, token["fee"])
                sellAmount = sellAmount / 10**token["decimals"]
                sellPrice =  MONEY / sellAmount
            except Exception as e:
                rawprice = uniswap.get_raw_price(Web3.toChecksumAddress(token["contract"]), ETH)
                buyPrice = float(eth_price) * rawprice
                buyAmount = 0
                sellAmount = 0
                sellPrice = float(eth_price) * rawprice
                pass


            try:
                coinbase = ccxt.coinbase()
                coinbase.load_markets()
            except Exception as e:
                pass
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
            print("")
            count = count + 1
        print("------")
    except Exception as e:
        print(e)
        errCount = errCount + 1
        time.sleep(120)
        pass
    time.sleep(5)
