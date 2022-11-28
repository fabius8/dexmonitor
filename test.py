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
version = 3                      # specify which version of Uniswap to use
provider = "https://rpc.ankr.com/eth"    # can also be set through the environment variable `PROVIDER`
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)
print("init...")

SOL = "0xD31a59c85aE9D8edEFeC411D448f90841571b89c"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

buyAmount = uniswap.get_price_input(USDT, SOL, 1 * 10**18, 3000)
print(buyAmount / 10**9)