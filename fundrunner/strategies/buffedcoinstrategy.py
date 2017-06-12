from .strategy import Strategy
import numpy as np
from .utils import initial_trades_equal_alloc, rebalancing_trades_equal_alloc, held_coins_with_chart_data
from .utils import is_buffed

def find_buffed_coins (chart_data, balances):
    # if we hold other stuff,
    est_values = balances.estimate_values(chart_data)
    print(est_values)
    buffed_coins = [
      coin for coin in held_coins_with_chart_data(chart_data, balances)
      if is_buffed(coin, est_values)
      # if is_buffed_fancy(coin, est_values)
      # if is_buffed_fancy2(coin, est_values)
    ]
    return buffed_coins

class BuffedCoinStrategy (Strategy):

  def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    # First of all, if we only hold fiat,
    if current_balances.held_coins() == [fiat]:
        # Make initial trades
        return initial_trades_equal_alloc(current_chart_data, current_balances, fiat)
    # If we do have stuff other than fiat,
    # see if any of those holdings are buffed
    buffed_coins = find_buffed_coins(current_chart_data, current_balances)
    print("BUFFED COINS: ", buffed_coins)
    # if any of them are,
    if len(buffed_coins):
        # sell them so as to reallocate their value eqaully
        return rebalancing_trades_equal_alloc(buffed_coins, current_chart_data,
                                              current_balances, fiat)
    return []
