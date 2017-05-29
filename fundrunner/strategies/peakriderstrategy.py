from .strategy import Strategy
from .utils import initial_trades_equal_alloc, rebalancing_trades_equal_alloc, held_coins_with_chart_data
from .utils import is_buffed, is_buffed_by_power, latest_ppo_hist

def find_buffed_coins (chart_data, balances):
    # if we hold other stuff,
    est_values = balances.estimate_values(chart_data)
    buffed_coins = [
      coin for coin in held_coins_with_chart_data(chart_data, balances)
        if is_buffed_by_power(coin, est_values)
    ]
    return buffed_coins


class PeakRiderStrategy (Strategy):

  def is_crashing (self, coin, time,
                   threshold=-0.15):
      if coin == self.fiat:
          currency_pair = 'USD_' + self.fiat
      else:
          currency_pair = '{!s}_{!s}'.format(self.fiat, coin)
      prices = self.coinstore.market_history(currency_pair, time)
      latest = latest_ppo_hist(prices)
      if latest > threshold:
          return True
      return False

  def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    # First of all, if we only hold fiat,
    if current_balances.held_coins() == [fiat]:
        # Make initial trades
        return initial_trades_equal_alloc(current_chart_data, current_balances, fiat)
    # If we do have stuff other than fiat,
    # see if any of those holdings are buffed
    buffed_coins = find_buffed_coins(current_chart_data, current_balances)
    buffed_and_crashing = [coin for coin in buffed_coins
                           if self.is_crashing(coin, current_balances.time) ]
    # if any of them are,
    if len(buffed_and_crashing):
        # sell them so as to reallocate their value eqaully
        return rebalancing_trades_equal_alloc(buffed_and_crashing, current_chart_data,
                                              current_balances, fiat)
    return []
