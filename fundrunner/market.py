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

  def buy_coin(self, coin, amount):
    market = 'BTC_'+coin
    lowest_ask   = float(self.polo.returnTicker()[market]['lowestAsk'])
    # amount       = amount/float(lowest_ask)
    print("BUY", coin, amount)
    res = self.polo.buy(market, lowest_ask, amount)
    sleep(1)
    _, coin_pairs = self.cancel_open_orders()
    # if we canceled some order
    if coin_pairs is not None:
        for coin_pair in coin_pairs:
            # Recursively rebuy
            return self.buy_coin(coin, amount)
    return

  # String, Float -> None
  def sell_coin (self, coin, amount):
      '''
      Sell some amount of non-BTC `coin` for BTC.
      Will retry until it sucessfuly executes the trade at the best price.
      '''
      # Place an order
      market = 'BTC_'+coin
      highest_bid = float(self.polo.returnTicker()[market]['highestBid'])
      # logging.info('Placing order to sell %s %s at %s BTC',
            # amount, coin, highest_bid)
      print("SELL", coin, amount)
      res = self.polo.sell(market, highest_bid, amount)
      # Wait, then see if any orders still open
      sleep(1)
      _, coin_pairs = self.cancel_open_orders()
      # if we canceled some order
      if coin_pairs is not None:
          for coin_pair in coin_pairs:
              # Recursively rebuy
              return self.sell_coin(coin, amount)
      return

  def make_purchase(self, purchase, fiat='BTC'):
    """ Performs a purchase on the market given a source coin, destination coin,
        and amount in each.  Returns the real purchase amount, which may not be
        exactly the same as the requested purchase amount.
        function(Purchase) -> Purchase
    """
    if purchase.from_coin == fiat:
      market = fiat + "_" + purchase.to_coin
      rate = purchase.from_amount / purchase.to_amount
      print("BUY", market, purchase.to_amount)
      # market, (FIAT / OTHER), OTHER
      if purchase.from_amount > 0.0001:
        return self.polo.buy(market, rate, purchase.to_amount)
    elif purchase.to_coin == fiat:
      market = fiat + "_" + purchase.from_coin
      rate = purchase.to_amount / purchase.from_amount
      print("SELL", market, purchase.to_amount)
      # market, (FIAT / OTHER), OTHER
      if purchase.to_amount > 0.0001:
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
      if float(bal['btcValue']) > 0:
        all_balances[coin] = float(bal['btcValue'])
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

  # Needs a sanity check....
  def redistribute_evenly (self):
    markets = self.get_btc_markets()
    bals = self.get_balances()
    sum_total = pd.Series(bals).sum()
    inv_per_coin = sum_total / len(markets)
    ticker = self.polo.returnTicker()
    to_sell = {}
    to_buy = {}
    for coin, btcValue, in bals.items():
      if btcValue > 0:
        if btcValue > inv_per_coin:
          if coin != 'BTC':
            btc_amount = btcValue - inv_per_coin
            lowestAsk = float(ticker['BTC_' + coin]['lowestAsk'])
            coinToSell = btc_amount / lowestAsk
            if btc_amount > 0.0001:
              to_sell[coin] = coinToSell
        else:
          if coin != 'BTC':
            btc_amount = inv_per_coin - btcValue
            lowestAsk = float(ticker['BTC_' + coin]['lowestAsk'])
            coinToBuy = btc_amount / lowestAsk
            if btc_amount > 0.0001:
              to_buy[coin] = coinToBuy
    # Sell coins
    for coin, amount, in to_sell.items():
      self.sell_coin(coin, amount)
    # Buy coins
    for coin, amount, in to_buy.items():
      self.buy_coin(coin, amount)




