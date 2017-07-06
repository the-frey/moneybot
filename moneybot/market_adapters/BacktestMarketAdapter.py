# -*- coding: utf-8 -*-
from typing import Iterator

from moneybot.market_adapters import MarketAdapter
from moneybot.MarketState import MarketState
from moneybot.ProposedTrade import ProposedTrade


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
