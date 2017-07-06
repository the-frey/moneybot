from typing import Tuple, Dict
from .BuffedCoinStrategy import BuffedCoinStrategy
import numpy as np
import pandas as pd


class PeakRiderStrategy (BuffedCoinStrategy):

    def emas (self, price_series: pd.Series,
              shortw=96, longw=2400, **kwargs) -> Tuple[pd.Series, pd.Series]:
        long_ema  = price_series.ewm(com=longw).mean()
        short_ema = price_series.ewm(com=shortw).mean()
        return long_ema, short_ema


    def percentage_price_oscillator (self, price_series: pd.Series,
                                     **kwargs) -> pd.Series:
        longe, shorte = self.emas(price_series, **kwargs)
        ppo           = (shorte - longe) / longe
        return ppo


    def ppo_histogram (self, price_series: pd.Series,
                       **kwargs) -> pd.DataFrame:
        ppo           = self.percentage_price_oscillator(price_series)
        ppo_ema       = ppo.ewm(com=9).mean()
        ppo_hist      = pd.DataFrame(ppo - ppo_ema)
        return ppo_hist


    def latest_ppo_hist (self, price_series: pd.Series) -> float:
        ppo_hist = self.ppo_histogram(price_series)
        latest   = ppo_hist.iloc[-1].values[0]
        return latest


    def is_buffed (self, coin: str, coin_values: Dict[str, float]) -> bool:
        # HACK HACK HACK HACK HACK
        # HACK magic number HACK
        # HACK HACK HACK HACK HACK
        POWER_OF = 1.2
        median_value  = self.median(coin_values)
        if median_value > 1:
            median_to_power = pow(median_value, POWER_OF)
        else:
            median_to_power = pow(median_value, 1 / POWER_OF)
            val = coin_values[coin]
            if val > median_to_power:
                return True
        return False


    def is_crashing (self, coin, time, market_history):
        if coin == self.fiat:
            prices = market_history.asset_history(time, 'USD', self.fiat)
        else:
            prices = market_history.asset_history(time, self.fiat, coin)
            latest = self.latest_ppo_hist(prices)
            if latest > 0:
                return True
            return False


    def propose_trades (self, market_state, market_history):
        # First of all, if we only hold fiat,
        if market_state.only_holding(self.fiat):
            # Make initial trades
            return self.initial_proposed_trades(market_state)
        # If we do have stuff other than fiat,
        # see if any of those holdings are buffed
        buffed_coins = self.find_buffed_coins(market_state)
        buffed_and_crashing = [coin for coin in buffed_coins
                               if self.is_crashing(coin, market_state.time, market_history) ]
        # if any of them are,
        if len(buffed_and_crashing):
            # sell them so as to reallocate their value eqaully
            proposed = self.rebalancing_proposed_trades(buffed_and_crashing, market_state)
            return proposed
        return
