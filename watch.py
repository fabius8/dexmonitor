import ccxt.pro
from asyncio import run, gather

print('CCXT Pro version', ccxt.pro.__version__)

def table(values):
    first = values[0]
    keys = list(first.keys()) if isinstance(first, dict) else range(0, len(first))
    widths = [max([len(str(v[k])) for v in values]) for k in keys]
    string = ' | '.join(['{:<' + str(w) + '}' for w in widths])
    return "\n".join([string.format(*[str(v[k]) for k in keys]) for v in values])

async def watch_order_book(exchange, symbol):
    while True:
        try:
            orderbook = await exchange.watch_order_book(symbol)
            datetime = exchange.iso8601(exchange.milliseconds())
            #print(datetime, orderbook['nonce'], symbol, orderbook['asks'][0], orderbook['bids'][0])
        except Exception as e:
            print(type(e).__name__, str(e))
            break

async def watch_ohlcv(exchange, symbol):
    while True:
        try:
            timeframe = '1m' 
            limit = 3
            # 当前k线不算
            since = exchange.milliseconds() - (limit) * exchange.parse_timeframe(timeframe) * 1000
            ohlcvs = await exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            now = exchange.milliseconds()
            print('\n===============================================================================')
            print('Loop iteration:', 'current time:', exchange.iso8601(now), symbol, timeframe)
            print('-------------------------------------------------------------------------------')
            print(ohlcvs)
        except Exception as e:
            print(type(e).__name__, str(e))
            break

async def reload_markets(exchange, delay):
    while True:
        try:
            await exchange.sleep(delay)
            markets = await exchange.load_markets(True)
            datetime = exchange.iso8601(exchange.milliseconds())
            print(datetime, 'Markets reloaded')
        except Exception as e:
            print(type(e).__name__, str(e))
            break


async def main():
    exchange = ccxt.pro.binance()
    await exchange.load_markets()
    # exchange.verbose = True
    symbol = 'BTC/USDT'
    delay = 60000  # every minute = 60 seconds = 60000 milliseconds
    loops = [watch_ohlcv(exchange, symbol)]
    await gather(*loops)
    await exchange.close()


run(main())