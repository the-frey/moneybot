# -*- coding: utf-8 -*-
from abc import ABCMeta
from abc import abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Dict
from typing import Generator
from typing import Iterator
from typing import List

from moneybot.market.history import MarketHistory
from moneybot.market.state import MarketState
from moneybot.strategy import ProposedTrade


logger = getLogger(__name__)


class MarketAdapter(metaclass=ABCMeta):

    def __init__(
        self,
        history: MarketHistory,
        initial_balances: Dict[str, float],
        fiat: str,
    ) -> None:
        self.market_history = history
        self.balances = initial_balances
        self.fiat = fiat

    @abstractmethod
    def get_balances(self):
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        proposed_trades: Iterator[ProposedTrade],
        market_state: MarketState,
    ):
        raise NotImplementedError

    def get_market_state(self, time: datetime) -> MarketState:
        # Get the latest chart data from the market
        charts = self.market_history.latest(time)
        balances = self.get_balances()
        # We wrap these data in a MarketState,
        # which provides some convenience methods.
        market_state = MarketState(charts, balances, time, self.fiat)
        return market_state

    def filter_legal(
        self,
        proposed_trades: List[ProposedTrade],
        market_state: MarketState,
    ) -> Generator[ProposedTrade, None, None]:
        '''
        Takes a list of ProposedTrade objects.
        Checks that each is a legal trade by the rules of our market.
        '''
        for proposed in proposed_trades:
            if self.is_legal(proposed, market_state):
                yield proposed

    def is_legal(
        self,
        proposed: ProposedTrade,
        market_state: MarketState,
    ) -> bool:
        # TODO This is pretty Poloniex specific, so we might move it
        #      to a PoloniexMarketAdapter if we ever add more exchanges.

        # Check that proposed bid has a price:
        if not proposed.price:
            logger.warning(
                f'Filtering out proposed trade (has no price): {proposed}.'
            )
            return False

        # Check that we have enough to sell
        held_amount = market_state.balances[proposed.from_coin]
        if proposed.bid_amount > held_amount:
            logger.warning(
                "Filtering out proposed trade (can't sell more than is held): "
                f"{proposed}. Holding {held_amount} {proposed.from_coin}."
            )
            return False

        # Check that we are trading a positive amount for a positive amount
        if proposed.bid_amount < 0 or proposed.ask_amount < 0:
            logger.warning(
                'Filtering out proposed trade (bid or ask amount < 0): '
                f'{proposed}.'
            )
            return False

        # Check that the proposed trade exceeds minimum fiat trade amount.
        if (
            (proposed.from_coin == proposed.fiat and proposed.bid_amount < 0.0001) or
            (proposed.to_coin == proposed.fiat and proposed.ask_amount < 0.0001)
        ):
            logger.warning(
                'Filtering out proposed trade (transaction too small): '
                f'{proposed}.'
            )
            return False

        # Check that the trade is on a market that exists.
        if proposed.market_name not in market_state.chart_data.keys():
            logger.warning(
                f'Filtering out proposed trade (unknown market): {proposed}.'
            )
            return False

        return True
