from typing import Set, Dict, List, Generator
from ..ProposedTrade import ProposedTrade
from ..MarketHistory import MarketHistory
from ..MarketState import MarketState
from datetime import datetime
from time import sleep
import pandas as pd

ProposedTradeGenerator = Generator[ProposedTrade, None, None]


class Strategy (object):

    '''
    TODO Docstring
    how this is meant to be subclassed
    '''

    def __init__ (self, config: Dict) -> None:
        self.config = config
        self.fiat = config['fiat']
        # Interval between trades, in seconds
        self.trade_interval = config['trade_interval']
        # # MarketHistory stores historical market data
        # self.MarketHistory = MarketHistory(self.config)
        # # MarketAdapter executes trades, fetches balances
        # self.MarketAdapter = MarketAdapter(self.config)

    def propose_trades (self, market_state: MarketState, market_history: MarketHistory) -> List[ProposedTrade]:
        raise NotImplementedError


    '''
    Trade proposal utilities
    '''

    def _possible_investments (self, market_state: MarketState) -> Set[str]:
        '''
        Returns a set of all coins that the strategy might invest in,
        not including the fiat.
        '''
        return market_state.available_coins() - set([ self.fiat ])


    def _propose_trades_to_fiat (self,
                                 coins: List[str],
                                 fiat_value_per_coin: float,
                                 market_state: MarketState) -> ProposedTradeGenerator:
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


    def _propose_trades_from_fiat (self,
                                   coins: Set[str],
                                   fiat_investment_per_coin: float,
                                   market_state: MarketState) -> ProposedTradeGenerator:
        for coin in coins:
            proposed = ProposedTrade(self.fiat, coin)
            proposed.set_bid_amount(fiat_investment_per_coin, market_state)
            yield proposed


    def initial_proposed_trades (self, market_state: MarketState) -> ProposedTradeGenerator:
        '''
        "Initial" purchases are from fiat.
        (We assume funds start with only a fiat balance.)
        The resulting proposed trades should result in an equal allocation (of value, in fiat)
        across all "reachable" markets (markets in which the base currency is fiat).
        '''
        possible_investments = self._possible_investments(market_state)
        fiat_investment_per_coin = market_state.balances[self.fiat] / ( len(possible_investments) + 1.0 )
        trades = self._propose_trades_from_fiat(possible_investments,
                                                fiat_investment_per_coin,
                                                market_state)
        return trades



    def rebalancing_proposed_trades (self,
                                     coins_to_rebalance: List[str],
                                     market_state: MarketState) -> List[ProposedTrade]:

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
            fiat_after_trades        = est_bals_after_fiat_trades[self.fiat]
            to_redistribute          = fiat_after_trades - ideal_fiat_value_per_coin
            coins_divested_from      = [ proposed.from_coin for proposed in proposed_trades_to_fiat]
            coins_to_buy             = possible_investments - set(coins_divested_from) - set( [self.fiat] )
            to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
            proposed_trades_from_fiat = self._propose_trades_from_fiat(coins_to_buy,
                                                                       to_redistribute_per_coin,
                                                                       market_state)
            trades = proposed_trades_to_fiat + list(proposed_trades_from_fiat)

            return trades

        return proposed_trades_to_fiat
