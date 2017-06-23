from .strategy import Strategy
from .utils import initial_purchases_equal_alloc

class BuyHoldStrategy(Strategy):
  def get_purchases (self, current_chart_data, current_balances, fiat='BTC'):
    if current_balances.held_coins() == [fiat]:
      # buy some stuff
      return initial_purchases_equal_alloc(current_chart_data, current_balances, fiat)
    # if we hold things other than BTC, hold
    # hold
    return []
