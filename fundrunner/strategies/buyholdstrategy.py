from ..strategy import Strategy

class BuyHoldStrategy(Strategy):
  def propose_trades (self, market_state):
    if market_state.only_holding(self.fiat):
      # buy some stuff
      return self.initial_proposed_trades(market_state)
    # if we hold things other than BTC, hold
    # hold
    return []
