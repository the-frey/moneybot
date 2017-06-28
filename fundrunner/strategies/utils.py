from ..proposedtrade import ProposedTrade
import numpy as np
import pandas as pd

'''
Generic utils
'''

def coin_names (market_name):
    coins = market_name.split('_')
    return coins[0], coins[1]

def available_markets (chart_data, fiat):
    return set([ k for k in chart_data.keys() if k.startswith(fiat) ])

def held_coins_with_chart_data (chart_data, balances,
                                fiat='BTC'):
    avail_markets = available_markets(chart_data, fiat)
    # Extract the coin name from each available fiat-to-coin market
    avail_coins   = [coin_names(market)[1] for market in avail_markets]
    # The fiat is always available, so we'll add that to the list as well
    avail_coins  += [fiat]
    return set(balances.held_coins()).intersection(avail_coins)


'''
Initial allocation tools
'''

def initial_proposed_trades_equal_alloc (chart_data, balances, fiat):
    '''
    "Initial" purchases are from fiat.
    (We assume funds start with only a fiat balance.)
    The resulting proposed trades should result in an equal allocation (of value, in fiat)
    across all "reachable" markets (markets in which the base currency is fiat).
    '''
    avail = available_markets(chart_data, fiat)
    fiat_investment_per_coin = balances[fiat] / ( len(avail) + 1.0 )
    proposed_trades = []
    for market in avail:
        to_coin = coin_names(market)[1]
        # Trade from fiat to whatever coin
        proposed = ProposedTrade(fiat, to_coin)
        # Find the price of that coin, in fiat
        # TODO This seems like somebody else's job - and we don't need to do it right now
        proposed = proposed.estimate_price(chart_data)
        # How much fiat to sell?
        proposed = proposed.set_bid_amount(fiat_investment_per_coin)
        proposed_trades.append(proposed)
    return proposed_trades

'''
Rebalancing tools
'''

def propose_trades_to_fiat (coins, ideal_fiat_value_per_coin,
                            chart_data, balances, fiat):
    for coin in coins:
        if coin != fiat:
            # Sell coin for fiat
            proposed = ProposedTrade(coin, fiat)
            # Get the coin's price, in fiat
            proposed = proposed.estimate_price(chart_data)
            # After rebalance, we want the value of the coin we're trading to
            # to be equal to the ideal value (in fiat).
            # First we'll find the value of the coin we currently hold.
            current_coin_value_fiat = (balances[coin] * proposed.price)
            # To find how much coin we want to sell,
            # we'll subtract our holding's value from the ideal value
            # to produce the value of coin we must sell
            value_to_sell = current_coin_value_fiat - ideal_fiat_value_per_coin
            # Now we find the amount of coin equal to this value
            amount_to_sell = value_to_sell / proposed.price
            if amount_to_sell > 0:
                proposed = proposed.set_bid_amount(amount_to_sell)
                yield proposed

def propose_trades_from_fiat (coins, investment_per_coin, chart_data, balances, fiat):
    for coin in coins:
        proposed = ProposedTrade(fiat, coin)
        proposed = proposed.estimate_price(chart_data)
        proposed = proposed.set_bid_amount(investment_per_coin)
        yield proposed


def rebalancing_proposed_trades_equal_alloc (coins_to_rebalance, chart_data, balances, fiat):

    avail = available_markets(chart_data, fiat)
    total_value = balances.estimate_total_fiat_value(chart_data)
    ideal_fiat_value_per_coin = total_value / len(avail) # TODO maybe +1? like above?

    proposed_trades_to_fiat = list(propose_trades_to_fiat(coins_to_rebalance,
                                                          ideal_fiat_value_per_coin,
                                                          chart_data,
                                                          balances,
                                                          fiat))

    # Next, we will simulate actually executing all of these trades
    # Afterward, we'll get some simulated balances
    # TODO apply_purchaess should really be some kind of Simulate or whatever in a market adapter
    est_bals_after_fiat_trades = balances.apply_purchases(proposed_trades_to_fiat)

    if fiat in coins_to_rebalance and len(proposed_trades_to_fiat) > 0:
        fiat_after_trades        = est_bals_after_fiat_trades[fiat]
        to_redistribute          = fiat_after_trades - ideal_fiat_value_per_coin
        markets_divested_from    = [fiat + '_' + proposed.from_coin
                                    for proposed in proposed_trades_to_fiat]
        markets_to_buy           = set(avail) - set(markets_divested_from)
        coins_to_buy             = [coin_names(m)[1] for m in markets_to_buy]
        to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
        proposed_trades_from_fiat = propose_trades_from_fiat(coins_to_buy,
                                                             to_redistribute_per_coin,
                                                             chart_data,
                                                             balances,
                                                             fiat)
        return proposed_trades_to_fiat + list(proposed_trades_from_fiat)

    return proposed_trades_to_fiat


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


'''
is_crashing tools
'''
# PandasSeries -> (PandasSeries, PandasSeries)
def emas (price_series, shortw=96, longw=2400, **kwargs):
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
