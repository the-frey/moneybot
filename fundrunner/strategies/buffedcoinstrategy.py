from ..strategy import Strategy
import numpy as np


class BuffedCoinStrategy (Strategy):

    def median (self, est_values):
        return np.median(list(est_values.values()))


    def is_buffed (self, coin, coin_values):
        # HACK HACK HACK HACK HACK
        # HACK magic number HACK
        # HACK HACK HACK HACK HACK
        MULTIPLIER = 1.5
        median_value  = self.median(coin_values)
        if coin_values[coin] > (median_value * MULTIPLIER):
            return True
        return False


    def find_buffed_coins (self, chart_data, balances):
        # if we hold other stuff,
        est_values = balances.estimate_values(chart_data)
        buffed_coins = [
            coin for coin in self.held_coins_with_chart_data(chart_data, balances)
            if self.is_buffed(coin, est_values)
            # if is_buffed_fancy(coin, est_values)
            # if is_buffed_fancy2(coin, est_values)
        ]
        return buffed_coins

    def propose_trades (self, current_chart_data, current_balances, time):
        # First of all, if we only hold fiat,
        if current_balances.held_coins() == [self.fiat]:
            return self.initial_proposed_trades(current_chart_data, current_balances)
        # If we do have stuff other than fiat,
        # see if any of those holdings are buffed
        buffed_coins = self.find_buffed_coins(current_chart_data, current_balances)
        # if any of them are,
        if len(buffed_coins):
            # sell them so as to reallocate their value eqaully
            return self.rebalancing_proposed_trades(buffed_coins, current_chart_data, current_balances)
        return []
