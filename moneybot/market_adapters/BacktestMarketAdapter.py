from typing import Iterator
from . import MarketAdapter
from ..ProposedTrade import ProposedTrade
from ..MarketState import MarketState

class BacktestMarketAdapter (MarketAdapter):

    def get_balances (self) -> None:
        return self.balances

    def execute (self,
                 proposed_trades: Iterator[ProposedTrade],
                 market_state: MarketState) -> None:
        balances = market_state.simulate_trades(proposed_trades)
        self.balances = balances

