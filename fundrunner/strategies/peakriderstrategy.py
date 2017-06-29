from .buffedcoinstrategy import BuffedCoinStrategy
import numpy as np
import pandas as pd

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

class PeakRiderStrategy (BuffedCoinStrategy):

    def is_buffed (self, coin, coin_values, power_of = 1.2):
        median_value  = self.median(coin_values)
        if median_value > 1:
            median_to_power = pow(median_value, power_of)
        else:
            median_to_power = pow(median_value, 1/power_of)
            val = coin_values[coin]
            if val > median_to_power:
                return True
        return False


    def is_crashing (self, coin, time):
        # TODO You'd think the coinstore could have a method market_history(base, quote)
        #      so I wouldn't have to manipulate strings.....
        #      Again, this is something for a MarketAdapter
        if coin == self.fiat:
            prices = self.MarketHistory.asset_history(time, 'USD', self.fiat)
        else:
            prices = self.MarketHistory.asset_history(time, self.fiat, coin)
            latest = latest_ppo_hist(prices)
            if latest > 0:
                return True
            return False


    def propose_trades (self, current_chart_data, current_balances, time):
        # First of all, if we only hold fiat,
        if current_balances.held_coins() == [self.fiat]:
            # Make initial trades
            return self.initial_proposed_trades(current_chart_data, current_balances)
        # If we do have stuff other than fiat,
        # see if any of those holdings are buffed
        buffed_coins = self.find_buffed_coins(current_chart_data, current_balances)
        buffed_and_crashing = [coin for coin in buffed_coins
                               if self.is_crashing(coin, time) ]
        # if any of them are,
        if len(buffed_and_crashing):
            # sell them so as to reallocate their value eqaully
            proposed = self.rebalancing_proposed_trades(buffed_and_crashing, current_chart_data, current_balances)
            return proposed
        return []
