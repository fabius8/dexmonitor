import ccxt
import json
import time
from datetime import datetime
from decimal import Decimal


binance_spot = ccxt.binance({'options':{'defaultType':'spot'}})
markets_spot = binance_spot.load_markets()
binance_future = ccxt.binance({'options':{'defaultType':'future'}})
markets_future = binance_future.load_markets()

pair_spot = []
for i in markets_spot:
    if "/USDT" in i or "/BUSD" in i:
        pair_spot.append(i)
#print(pair_spot)

pair_future = []
for i in markets_future:
    if "/USDT" in i or "/BUSD" in i:
        pair_future.append(i)

for i in pair_future:
    if "/BUSD" in i:
        if (i[:-5] + "/USDT") in pair_future:
            pair_future.remove(i)
            continue
    if i not in pair_spot:
        pair_future.remove(i)

for i in pair_future:
    if i not in pair_spot:
        pair_future.remove(i)

if "FTT/USDT" in pair_future:
    pair_future.remove("FTT/USDT")
#print(pair_future, len(pair_future))

print(pair_future)
while True:
    try:
        timeframe = '1m'
        limit = 1
        need_diff = -0.005 * 100
        count = 0
        for symbol in pair_future:
            count = count + 1
            data = binance_future.fetch_funding_rate(symbol)
            funding_rate = Decimal(data["info"]["lastFundingRate"]) * 100
            ohlcvs_future = binance_future.fetch_ohlcv(symbol, timeframe, None, limit)
            if "HNT/USDT" == symbol:
                symbol = "HNT/BUSD"
            ohlcvs_spot = binance_spot.fetch_ohlcv(symbol, timeframe, None, limit)
            
            open_future = ohlcvs_future[0][1]
            high_future = ohlcvs_future[0][2]
            low_future  = ohlcvs_future[0][3]
            close_future = ohlcvs_future[0][4]

            open_spot = ohlcvs_spot[0][1]
            high_spot = ohlcvs_spot[0][2]
            low_spot  = ohlcvs_spot[0][3]
            close_spot = ohlcvs_spot[0][4]
            #print(ohlcvs_future, ohlcvs_spot)
            cur_diff = 100 * (close_future - close_spot)/close_spot
            
            print(binance_spot.iso8601(ohlcvs_spot[0][0]), "::", '{0:>5}'.format(str(count)),'{0:>16}'.format(symbol), \
                '{0:>8.2%}'.format(cur_diff/100), '{0:>19}'.format(str(funding_rate)), \
                '{0:<16}'.format("sp: " + str(close_spot)), "fp:", close_future)

            if (cur_diff < need_diff and close_future < open_future):
                print("loan create")
            time.sleep(1)
    except Exception as e:
        print(type(e).__name__, str(e))
        #time.sleep(60)
        pass