from ..strategy import Strategy

class BuyHoldStrategy(Strategy):
  def propose_trades (self, current_chart_data, current_balances, time):
    if current_balances.held_coins() == [self.fiat]:
      # buy some stuff
      return self.initial_proposed_trades(current_chart_data, current_balances)
    # if we hold things other than BTC, hold
    # hold
    return []
