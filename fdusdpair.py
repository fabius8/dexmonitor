import ccxt
import json
import time
from datetime import datetime, timezone, timedelta

# 读取API密钥
secret = json.load(open('secret.json'))
binance = ccxt.binance(secret["binance"])
binance.load_markets()

symbol = "FDUSD/USDT"
per_amount = 20000
errCount = 0
max_retries = 5
min_volume_threshold = 50 * 10000  # 50万 FDUSD
sleep_time = 5  # 轮询间隔

# 异常波动检测阈值（例如波动超过50%）
volume_decrease_threshold = 0.5

# 保存前一次的买一卖一委托量
previous_bid0_v = None
previous_ask0_v = None

# 重新连接交易所并加载市场数据
def reset_binance():
    global binance
    binance = ccxt.binance(secret["binance"])
    binance.load_markets()

# 获取总资产（USDT 和 FDUSD 折算成 USD）
def get_total_balance(balance, bid_price):
    total_usd = 0
    for asset in balance["info"]["balances"]:
        asset_free = float(asset["free"])
        asset_locked = float(asset["locked"])
        if asset['asset'] == "USDT":
            total_usd += asset_free + asset_locked
        elif asset['asset'] == "FDUSD":
            total_usd += (asset_free + asset_locked) * bid_price
    return total_usd

# 执行卖出 FDUSD 的操作
def sell_fdusd(balance, ask_price):
    for asset in balance["info"]["balances"]:
        if asset['asset'] == "FDUSD" and float(asset['free']) > 10.0:
            sell_amount = min(per_amount, float(asset['free']))
            sell_order = binance.createLimitSellOrder(symbol, sell_amount, ask_price)
            print_log(f"Sell Order: {sell_order['info']}")

# 执行买入 FDUSD 的操作
def buy_fdusd(balance, bid_price):
    for asset in balance["info"]["balances"]:
        if asset['asset'] == "USDT" and float(asset['free']) > 10.0:
            buy_amount = min(per_amount, float(asset['free']))
            buy_order = binance.createLimitBuyOrder(symbol, buy_amount, bid_price)
            print_log(f"Buy Order: {buy_order['info']}")

# 取消过期订单
def cancel_outdated_orders(open_orders, bid_price, ask_price):
    for order in open_orders:
        order_side = order["info"]["side"]
        order_price = float(order["info"]["price"])
        order_id = order["info"]["orderId"]
        if (order_side == "BUY" and order_price != bid_price) or (order_side == "SELL" and order_price != ask_price):
            cancel_order = binance.cancel_order(order_id, order["info"]["symbol"])
            print_log(f"Canceled {order_side} Order: {cancel_order['info']}")

# 取消特定类型的挂单（买单或卖单）
def cancel_orders_by_side(open_orders, side):
    for order in open_orders:
        order_side = order["info"]["side"]
        if order_side == side:
            order_id = order["info"]["orderId"]
            cancel_order = binance.cancel_order(order_id, order["info"]["symbol"])
            print_log(f"Ex Canceled {order_side} Order: {cancel_order['info']}")

# 检测委托量的异常波动并取消相关挂单
def detect_volume_spike_and_cancel_orders(bid0_v, ask0_v, open_orders):
    global previous_bid0_v, previous_ask0_v

    if previous_bid0_v is not None and previous_ask0_v is not None:
        # 计算买一和卖一的委托量变化率
        bid_change = (previous_bid0_v - bid0_v) / previous_bid0_v if previous_bid0_v != 0 and bid0_v < previous_bid0_v else 0
        ask_change = (previous_ask0_v - ask0_v) / previous_ask0_v if previous_ask0_v != 0 and ask0_v < previous_ask0_v else 0

        # 检测买一委托量的异常波动并取消买单
        if bid_change > volume_decrease_threshold:
            print_log(f"Warning: Bid volume spiked! Previous: {previous_bid0_v}, Current: {bid0_v}, Change: {bid_change*100:.2f}%")
            cancel_orders_by_side(open_orders, "BUY")  # 取消所有买单

        # 检测卖一委托量的异常波动并取消卖单
        if ask_change > volume_decrease_threshold:
            print_log(f"Warning: Ask volume spiked! Previous: {previous_ask0_v}, Current: {ask0_v}, Change: {ask_change*100:.2f}%")
            cancel_orders_by_side(open_orders, "SELL")  # 取消所有卖单

    # 更新前一次的委托量
    previous_bid0_v = bid0_v
    previous_ask0_v = ask0_v

# 打印带时间戳的日志
def print_log(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}")

while True:
    try:
        # 如果错误次数超过阈值，重置连接
        if errCount > max_retries:
            print_log("Max retries reached, resetting connection...")
            reset_binance()
            time.sleep(120)  # 等待两分钟
            errCount = 0

        # 获取订单簿数据
        order_book = binance.fetch_order_book(symbol)
        bid0_p, bid0_v = order_book['bids'][0]
        ask0_p, ask0_v = order_book['asks'][0]
        bid1_p = order_book['bids'][1][0]
        ask1_p = order_book['asks'][1][0]

        # 获取未完成的订单
        open_orders = binance.fetch_open_orders(symbol=symbol)

        # 检测买一卖一委托量的异常波动并取消相关挂单
        detect_volume_spike_and_cancel_orders(bid0_v, ask0_v, open_orders)

        # 判断买卖价是否使用买一卖一或买二卖二
        bid_price = bid1_p if bid0_v < min_volume_threshold else bid0_p
        ask_price = ask1_p if ask0_v < min_volume_threshold else ask0_p

        #print_log(f"Prices - Bid: {bid_price}, Ask: {ask_price}, Bid1: {bid1_p}, Ask1: {ask1_p}")

        # 获取余额并计算总资产
        balance = binance.fetch_balance()
        total_usd = get_total_balance(balance, bid0_p)
        #print_log(f"Total USD: {total_usd}")

        # 执行网格交易逻辑
        sell_fdusd(balance, ask_price)
        buy_fdusd(balance, bid_price)

        # 获取未完成的订单，并取消不符合当前价格的订单
        cancel_outdated_orders(open_orders, bid_price, ask_price)

    except Exception as e:
        print_log(f"Error: {e}")
        errCount += 1  # 计数错误次数
        pass

    time.sleep(sleep_time)
