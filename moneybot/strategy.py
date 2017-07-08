# -*- coding: utf-8 -*-
from abc import ABCMeta
from abc import abstractmethod
from logging import getLogger
from typing import Dict
from typing import Generator
from typing import List
from typing import Set

from moneybot.markets.history import MarketHistory
from moneybot.markets.state import MarketState


logger = getLogger(__name__)


class ProposedTrade:

    def __init__(
        self,
        from_coin: str,
        to_coin: str,
        fiat: str = 'BTC',
        fee: float = 0.0025,
    ) -> None:
        self.from_coin = from_coin
        self.to_coin = to_coin
        self.fiat = fiat
        self.price = 0.0
        self.ask_amount = 0.0
        self.bid_amount = 0.0
        self.fee = fee

        # get the Poloniex market name
        # Poloniex markets are named `{fiatSymol}_{quoteSymbol}`
        # By seeing whether from_ or to_ are the fiat,
        # we will construct the proper market name.
        # (yes, we can only trade directly fiat to/from fiat for now. sorry!)
        if from_coin == fiat:
            self.market_name = self._get_market_name(fiat, to_coin)
        elif to_coin == fiat:
            self.market_name = self._get_market_name(fiat, from_coin)

    def __str__(self) -> str:
        return '{!s} {!s} for {!s} {!s} (price of {!s} {!s}/{!s} on market {!s})'.format(
            self.bid_amount, self.from_coin,
            self.ask_amount, self.to_coin,
            self.price, self.from_coin, self.to_coin,
            self.market_name)

    '''
    Private methods
    '''

    def _get_market_name(
        self,
        base: str,
        quote: str,
    ) -> str:
        ''' Return Poloniex market name'''
        return f'{base}_{quote}'

    def _purchase_amount(
        self,
        investment: float,
        price: float,
    ) -> float:
        '''
        Private method.
        Get the amount of some coin purchased,
        given an investment (in quote), and a price (in quote),
        accounting for trading fees.
        '''
        in_amt = investment - (investment * self.fee)
        return in_amt / price

    '''
    Utility methods
    '''

    def estimate_price(self, market_state: MarketState):
        '''
        Sets the approximate price of the quote value, given some chart data.
        '''
        base_price = market_state.price(self.market_name)
        # The price (when buying/selling)
        # should match the self.market_name.
        # So, we keep around a self.market_price to match
        # self.price is always in the quote currency.
        self.market_price = base_price
        if self.to_coin == self.fiat:
            self.price = 1 / base_price
        else:
            self.price = base_price

    def set_bid_amount(
        self,
        amount: float,
        market_state: MarketState,
    ):
        '''
        Set how much `from_coin` we are putting on sale, by value.

        For convenience: we can estimate the price of the asset
        to set the `ask_amount` as well.
        When `self.estimate_price_with` is passed a `chart` object,
        it will pass this down to `estimate_price()`.
        '''
        if amount > market_state.balance(self.from_coin):
            self.bid_amount = market_state.balance(self.from_coin)
        else:
            self.bid_amount = amount

        self.estimate_price(market_state)
        self.ask_amount = self._purchase_amount(amount, self.price)

    def sell_to_achieve_value_of(
        self,
        desired_value: float,
        market_state: MarketState,
    ) -> None:
        '''
        Sets `self.bid_amount`, `self.ask_amount`, `self.price`
        such that the proposed trade would leave us with a
        holding of `desired_value`.
        '''
        self.estimate_price(market_state)
        if not self.price:
            logger.error(
                'Must set a price for ProposedTrade, or pass a chart object '
                'into estimate_price_with'
            )
            raise
        # After rebalance, we want the value of the coin we're trading to
        # to be equal to the ideal value (in fiat).
        # First we'll find the value of the coin we currently hold.
        current_value = market_state.balance(self.from_coin) * self.price
        # To find how much coin we want to sell,
        # we'll subtract our holding's value from the ideal value
        # to produce the value of coin we must sell
        value_to_sell = current_value - desired_value
        # Now we find the amount of coin equal to this value
        amount_to_sell = value_to_sell / self.price
        self.set_bid_amount(amount_to_sell, market_state)


class Strategy(metaclass=ABCMeta):
    '''
    TODO Docstring
    how this is meant to be subclassed
    '''

    def __init__(self, config: Dict) -> None:
        self.config = config
        self.fiat = config['fiat']
        # Interval between trades, in seconds
        self.trade_interval = config['trade_interval']
        # # MarketHistory stores historical market data
        # self.market_history = MarketHistory(self.config)
        # # MarketAdapter executes trades, fetches balances
        # self.market_adapter = MarketAdapter(self.config)

    @abstractmethod
    def propose_trades(
        self,
        market_state: MarketState,
        market_history: MarketHistory,
    ) -> List[ProposedTrade]:
        raise NotImplementedError

    '''
    Trade proposal utilities
    '''

    def _possible_investments(self, market_state: MarketState) -> Set[str]:
        '''
        Returns a set of all coins that the strategy might invest in,
        not including the fiat.
        '''
        return market_state.available_coins() - {self.fiat}

    def _propose_trades_to_fiat(
        self,
        coins: List[str],
        fiat_value_per_coin: float,
        market_state: MarketState,
    ) -> Generator[ProposedTrade, None, None]:
        for coin in coins:
            if coin != self.fiat:
                # Sell `coin` for `fiat`,
                # estimating how much `fiat` we should bid
                # (and how much `coin` we should ask for)
                # given the fiat value we want that coin to have after the trade
                proposed = ProposedTrade(coin, self.fiat)
                proposed.sell_to_achieve_value_of(fiat_value_per_coin, market_state)
                if proposed.bid_amount > 0:
                    yield proposed

    def _propose_trades_from_fiat(
        self,
        coins: Set[str],
        fiat_investment_per_coin: float,
        market_state: MarketState,
    ) -> Generator[ProposedTrade, None, None]:
        for coin in coins:
            proposed = ProposedTrade(self.fiat, coin)
            proposed.set_bid_amount(fiat_investment_per_coin, market_state)
            yield proposed

    def initial_proposed_trades(
        self,
        market_state: MarketState,
    ) -> Generator[ProposedTrade, None, None]:
        '''
        "Initial" purchases are from fiat.
        (We assume funds start with only a fiat balance.)
        The resulting proposed trades should result in an equal allocation (of value, in fiat)
        across all "reachable" markets (markets in which the base currency is fiat).
        '''
        possible_investments = self._possible_investments(market_state)
        fiat_investment_per_coin = market_state.balances[self.fiat] / (len(possible_investments) + 1.0)
        trades = self._propose_trades_from_fiat(possible_investments,
                                                fiat_investment_per_coin,
                                                market_state)
        return trades

    def rebalancing_proposed_trades(
        self,
        coins_to_rebalance: List[str],
        market_state: MarketState,
    ) -> List[ProposedTrade]:
        possible_investments = self._possible_investments(market_state)
        total_value = market_state.estimate_total_value()
        ideal_fiat_value_per_coin = total_value / len(possible_investments)

        proposed_trades_to_fiat = list(self._propose_trades_to_fiat(coins_to_rebalance,
                                                                    ideal_fiat_value_per_coin,
                                                                    market_state))

        # Next, we will simulate actually executing all of these trades
        # Afterward, we'll get some simulated balances
        est_bals_after_fiat_trades = market_state.simulate_trades(proposed_trades_to_fiat)

        if self.fiat in coins_to_rebalance and len(proposed_trades_to_fiat) > 0:
            fiat_after_trades = est_bals_after_fiat_trades[self.fiat]
            to_redistribute = fiat_after_trades - ideal_fiat_value_per_coin
            coins_divested_from = [proposed.from_coin for proposed in proposed_trades_to_fiat]
            coins_to_buy = possible_investments - set(coins_divested_from) - {self.fiat}
            to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
            proposed_trades_from_fiat = self._propose_trades_from_fiat(coins_to_buy,
                                                                       to_redistribute_per_coin,
                                                                       market_state)
            trades = proposed_trades_to_fiat + list(proposed_trades_from_fiat)

            return trades

        return proposed_trades_to_fiat
