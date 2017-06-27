from poloniex import Poloniex
import numpy as np
import pandas as pd
from . import Purchase
from time import sleep

class Market(object):
  def make_purchase(purchase):
    raise NotImplemented

class PoloniexMarket(Market):
  def __init__(self, pubkey, privkey):
    self.polo = Poloniex(pubkey, privkey)

    # TODO does this really return a purchase? I don't think so....
    # TODO helper method recursively buys, use immediateOrCancel
  def make_purchase(self, purchase, fiat='BTC'):
    """ Performs a purchase on the market given a source coin, destination coin,
        and amount in each.  Returns the real purchase amount, which may not be
        exactly the same as the requested purchase amount.

        If no purchase can be made (e.g. purchase too small), returns None.

        function(Purchase) -> Purchase
    """
    if not purchase:
      return None
    if purchase.from_coin == fiat:
      market = fiat + "_" + purchase.to_coin
      rate = purchase.from_amount / purchase.to_amount
      print("BUY", market, purchase.to_amount)
      # market, (FIAT / OTHER), OTHER
      return self.polo.buy(market, rate, purchase.to_amount)
    elif purchase.to_coin == fiat:
      market = fiat + "_" + purchase.from_coin
      rate = purchase.to_amount / purchase.from_amount
      print("SELL", market, purchase.to_amount)
      # market, (FIAT / OTHER), OTHER
      return self.polo.sell(market, rate, purchase.from_amount)

  def open_orders(self):
    open_orders = self.polo.returnOpenOrders()
    open_order_nums = [v[0]['orderNumber'] for v in open_orders.values() if len(v)]
    coins_to_try_again = [coin for coin, v in open_orders.items() if len(v)]
    return open_order_nums, coins_to_try_again

  def cancel_open_orders(self):
    open_order_ids, open_order_coins = self.open_orders()
    if len(open_order_ids) > 0:
        # cancel open orders
        print('canceling orders', open_order_coins)
        [self.polo.cancelOrder(order) for order in open_order_ids]
        return open_order_ids, open_order_coins
    return None, None

  def get_balances(self):
    bals = self.polo.returnCompleteBalances()
    all_balances = {}
    for coin, bal, in bals.items():
      avail = float(bal['available'])
      if  avail > 0:
        all_balances[coin] = avail
    return all_balances

  def get_btc_markets(self):
    ticker = self.polo.returnTicker()
    return [tick for tick in ticker if tick.startswith('BTC_')]

  def latest_chart_data(self, period=300):
    markets = self.get_btc_markets()
    latest_charts = {}
    for market in markets:
      latest_charts[market] = self.polo.returnChartData(market, period)[-1]
      latest_charts[market]['average'] = float(latest_charts[market]['weightedAverage'])
    return latest_charts
