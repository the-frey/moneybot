from .. import Trade
from .. import Purchase
import numpy as np
import pandas as pd

'''
Generic utils
'''

def coin_names (market_name):
    coins = market_name.split('_')
    return coins[0], coins[1]

def available_markets (chart_data):
    return set(chart_data.keys())

def held_coins_with_chart_data (chart_data, balances,
                                fiat='BTC'):
    avail_markets = available_markets(chart_data)
    # Extract the coin name from each available fiat-to-coin market
    avail_coins   = [coin_names(market)[1] for market in avail_markets]
    # The fiat is always available, so we'll add that to the list as well
    avail_coins  += [fiat]
    return set(balances.held_coins()).intersection(avail_coins)

def get_purchases (current_chart_data, trade,
                   fee=0.0025, fiat='BTC', price_key='average'):
    if trade.to_coin == fiat:
        market_name = '{!s}_{!s}'.format(fiat, trade.from_coin)
        to_price = 1 / current_chart_data[market_name][price_key]
    else:
        market_name = '{!s}_{!s}'.format(fiat, trade.to_coin)
        to_price = current_chart_data[market_name][price_key]
    from_investment = trade.from_amount - (trade.from_amount * fee)
    to_amount = from_investment / to_price
    return Purchase(trade.from_coin, trade.from_amount, trade.to_coin, to_amount)

'''
Initial allocation tools
'''

def initial_trades_equal_alloc (chart_data, balances, fiat):
    avail = available_markets(chart_data)
    amount_to_invest_per_coin = balances[fiat] / ( len(avail) + 1.0 )
    trades = [ Trade(fiat, amount_to_invest_per_coin, coin_names(market)[1])
               for market in avail ]
    return trades

'''
Rebalancing tools
'''

def rebalancing_trades_equal_alloc (coins_to_rebalance, chart_data, balances, fiat):
    avail = available_markets(chart_data)
    total_value = balances.estimate_total_fiat_value(chart_data)
    ideal_value_fiat = total_value / len(avail)
    # Note: Below estimates the trades, might not reflect real trades/purchases.
    trades_to_fiat = [ Trade(coin, balances[coin] - ideal_value_fiat, fiat)
                       for coin in coins_to_rebalance if coin != fiat ]
    fiat_purchases = [ get_purchases (chart_data, trade)
                       for trade in trades_to_fiat ]
    est_bals_after_fiat_trades = balances.apply_purchases(None, fiat_purchases)

    if fiat in coins_to_rebalance:
        fiat_after_trades        = est_bals_after_fiat_trades[fiat]
        to_redistribute          = fiat_after_trades - ideal_value_fiat
        markets_in_trades        = [fiat + '_' + trade.from_coin for trade in trades_to_fiat]
        markets_to_buy           = set(avail) - set(markets_in_trades)
        to_redistribute_per_coin = to_redistribute / len(markets_to_buy)
        trades_from_fiat         = [ Trade(fiat, to_redistribute_per_coin, coin_names(market)[1] )
                                    for market in markets_to_buy ]
        return trades_to_fiat + trades_from_fiat

    return trades_to_fiat

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
