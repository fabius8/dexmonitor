import ccxt

binance = ccxt.binance()
binance.load_markets()

busdPair = []
usdtPair = []
watchPair = []
for symbol in binance.markets:
    if "/BUSD" in symbol:
        sym = symbol.replace("/BUSD", "")
        busdPair.append(sym)
        
    if "/USDT" in symbol:
        sym = symbol.replace("/USDT", "")
        usdtPair.append(sym)
        
for sym in busdPair:
    if sym not in usdtPair:
        watchPair.append(sym)
        
print("BUSD:", len(busdPair))
print("USDT:", len(usdtPair))
print(watchPair, len(watchPair))