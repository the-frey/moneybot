# -*- coding: utf-8 -*-
from typing import Iterator

from moneybot.market.adapters import MarketAdapter
from moneybot.market.state import MarketState
from moneybot.strategy import ProposedTrade


class BacktestMarketAdapter(MarketAdapter):

    def get_balances(self):
        return self.balances

    def execute(
        self,
        proposed_trades: Iterator[ProposedTrade],
        market_state: MarketState,
    ):
        balances = market_state.simulate_trades(proposed_trades)
        self.balances = balances
