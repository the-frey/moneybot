from .EqualWeightIndexFund import EqualWeightIndexFund

class BuyHoldStrategy (EqualWeightIndexFund):

  def propose_trades (self, market_state):

    # If we only have BTC,
    if market_state.only_holding(self.fiat):
      # buy some stuff
      return self.initial_proposed_trades(market_state)

    # if we hold things other than BTC, hold.
    return
