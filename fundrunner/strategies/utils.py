from .. import Trade
from .. import Purchase
import numpy as np
import pandas as pd

'''
Generic utils
'''

def available_coins (chart_data):
    return set(chart_data.keys())

def held_coins_with_chart_data (chart_data, balances):
    avail = available_coins(chart_data)
    return set(balances.held_coins()).intersection(avail)

def get_purchase_amounts (current_chart_data, trade,
                          fee=0.0025, fiat='BTC', price_key='close'):
    if trade.to_coin == fiat:
        to_price = 1 / current_chart_data[trade.from_coin][price_key]
    else:
        to_price = current_chart_data[trade.to_coin][price_key]
    from_investment = trade.from_amount - (trade.from_amount * fee)
    to_amount = from_investment / to_price
    return Purchase(trade.from_coin, trade.from_amount, trade.to_coin, to_amount)

'''
Initial allocation tools
'''

def initial_trades_equal_alloc (chart_data, balances, fiat):
    avail_coins = available_coins(chart_data)
    amount_to_invest_per_coin = balances[fiat] / ( len(avail_coins) + 1.0 )
    trades = [ Trade(fiat, amount_to_invest_per_coin, c)
              for c in avail_coins if c != fiat ]
    return trades

'''
Rebalancing tools
'''

def rebalancing_trades_equal_alloc (coins_to_rebalance, chart_data, balances, fiat):
   avail_coins = available_coins(chart_data)
   total_value = balances.estimate_total_fiat_value(chart_data)
   ideal_value_fiat = total_value / len(avail_coins)
   # Note: Below estimates the trades, might not reflect real trades/purchases.
   trades_to_fiat = [ Trade(coin, balances[coin] - ideal_value_fiat, fiat)
                      for coin in coins_to_rebalance if coin != fiat ]
   fiat_purchases = [ get_purchase_amounts(chart_data, trade)
                      for trade in trades_to_fiat ]
   est_bals_after_fiat_trades = balances.apply_purchases(None, fiat_purchases)

   trades_from_fiat = []
   if fiat in coins_to_rebalance:
       fiat_after_trades        = est_bals_after_fiat_trades[fiat]
       coins_to_buy             = avail_coins - set([ fiat ]) - set(coins_to_rebalance)
       to_redistribute          = fiat_after_trades - ideal_value_fiat
       to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
       trades_from_fiat         = [ Trade(fiat, to_redistribute_per_coin, coin)
                                    for coin in coins_to_buy ]

   return trades_to_fiat + trades_from_fiat

'''
is_buffed tools
'''

def median (est_values):
    return np.median(list(est_values.values()))

def sum_of (est_values):
    return sum(list(est_values.values()))

def is_buffed (coin, coin_values,
               multiplier=2.0,
               ):
    median_value  = median(coin_values)
    if coin_values[coin] > (median_value * multiplier):
        return True
    return False

def is_buffed_by_power (coin, coin_values,
                        power_of = 1.2):
    median_value  = median(coin_values)
    if median_value > 1:
        median_to_power = pow(median_value, power_of)
    else:
        median_to_power = pow(median_value, 1/power_of)
    val = coin_values[coin]
    if val > median_to_power:
        return True
    return False

# def is_buffed_by_percent (coin, coin_values,
#                           threshold = 0.05):
#     # TODO: change this to use diff from ideal rather than mean
#     total_value = sum_of(coin_values)
#     pct_value = coin_values[coin] / total_value
#     pct_ideal = (1.0 / len(coin_values.keys()))
#     return abs(pct_value - pct_ideal) > threshold

'''
is_crashing tools
'''
# PandasSeries -> (PandasSeries, PandasSeries)
def emas (price_series, shortw=2, longw=25, **kwargs):
    long_ema  = price_series.ewm(com=longw).mean()
    short_ema = price_series.ewm(com=shortw).mean()
    return long_ema, short_ema

def percentage_price_oscillator (price_series, **kwargs):
    longe, shorte = emas(price_series, **kwargs)
    ppo           = (shorte - longe) / longe
    return ppo

# PandasSeries -> PandasSeries
def ppo_histogram (price_series, **kwargs):
    ppo           = percentage_price_oscillator(price_series)
    ppo_ema       = ppo.ewm(com=9).mean()
    ppo_hist      = pd.DataFrame(ppo - ppo_ema)
    return ppo_hist

def latest_ppo_hist (price_series):
    ppo_hist = ppo_histogram(price_series)
    latest   = ppo_hist.iloc[-1].values[0]
    return latest
