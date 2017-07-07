# -*- coding: utf-8 -*-
from typing import Iterator

from moneybot.markets.adapters import MarketAdapter
from moneybot.markets.proposed_trade import ProposedTrade
from moneybot.markets.state import MarketState


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
