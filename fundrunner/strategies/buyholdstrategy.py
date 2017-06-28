from ..strategy import Strategy
from .utils import initial_proposed_trades_equal_alloc

class BuyHoldStrategy(Strategy):
  def propose_trades (self, current_chart_data, current_balances, time):
    if current_balances.held_coins() == [self.fiat]:
      # buy some stuff
      return initial_proposed_trades_equal_alloc(current_chart_data, current_balances, self.fiat)
    # if we hold things other than BTC, hold
    # hold
    return []
