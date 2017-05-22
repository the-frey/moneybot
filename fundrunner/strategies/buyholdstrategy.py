from .strategy import Strategy
from .. import Trade

class BuyHoldStrategy(Strategy):
  def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    if current_balances.held_coins() == [fiat]:
      # buy some stuff
      available_coins = current_chart_data.keys()
      amount_to_invest_per_coin = current_balances[fiat] / ( len(available_coins) + 1.0 )
      trades = [ Trade(fiat, amount_to_invest_per_coin, c) 
                for c in available_coins if c != fiat ]
      return trades
    # if we hold things other than BTC, hold
    # hold
    return []
