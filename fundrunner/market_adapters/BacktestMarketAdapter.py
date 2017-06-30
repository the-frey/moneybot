from . import MarketAdapter

class BacktestMarketAdapter (MarketAdapter):

    def __init__ (self, config):
        self.balances = config['backtesting']['initial_balances']


    def get_balances (self):
        return self.balances


    def execute (self, proposed_trades, market_state):
        # Now, we will actually execute the trades.
        balances = market_state.simulate_trades(proposed_trades)
        self.balances = balances

