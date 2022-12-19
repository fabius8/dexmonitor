import ccxt.pro
import asyncio
import json
from datetime import datetime
import time
import random
import requests
import httpx

exchange = ccxt.binance()
exchange.load_markets()
symbols = [] 
def init():
    for symbol in exchange.markets:
        if "/USDT" in symbol:
            try:
                if len(symbols) > 500:
                    break
                order_book = exchange.fetch_order_book(symbol)
                order_book["bids"][0][0]
                symbols.append(symbol)
                print(symbol)
            except Exception as e:
                #print(e)
                pass

init()
print("监控", len(symbols), "个币", symbols)

secret = json.load(open('secret.json'))
async def sendToWechat(text):
    try:
        params = {
            "corpid": secret["weixin"]['corpid'],
            "corpsecret": secret["weixin"]['corpsecret']
        }
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params = params)
        access_token = r.json()["access_token"]
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
        params = {
            "access_token": access_token
        }
        data = {
            "touser": "@all",
            "msgtype" : "text",
            "agentid" : secret["weixin"]['agentid'],
            "text" : {
                "content" : text
            }
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(url, params = params, json = data)
    except Exception as e:
        print(e)
        pass


async def watch_loop(exchange, symbol, n):
    await asyncio.sleep(random.randint(1, 60))
    timeframe = '3m'
    limit = 1
    diff = 0.05
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, None, limit)
        #print(ohlcv)
        open = float(ohlcv[0][1])
        close = float(ohlcv[0][4])
        cur = (close - open) / open
        if abs(cur) >= diff:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '{0:>8}'.format(str(symbols.index(symbol)) + "/" + str(len(symbols))) + " " + '{0:>15}'.format(symbol), "价格波动超过", "{0:>8.2%}".format(cur))
            #微信通知
            text = "品种:" + symbol + "\n"
            text += "饺易所:" + str(exchange) + "\n"
            text += "k线周期:" + timeframe + "\n"
            text += "波动:" + format(cur, "+.2f") + "\n"
            await sendToWechat(text)
            

    except Exception as e:
        print(type(e).__name__, str(e), symbol)
        pass
   

async def main(exchange, symbols):
    print(symbols)
    while True:
        await asyncio.gather(*[watch_loop(exchange, symbol, n) for n, symbol in enumerate(symbols)])
        print("=" * 10)
        await asyncio.sleep(1)

exchange = ccxt.pro.binance()
asyncio.run(main(exchange, symbols))