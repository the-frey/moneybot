from typing import List, Generator
from ..MarketState import MarketState
from ..ProposedTrade import ProposedTrade

class MarketAdapter (object):

    def __init__ (self, market_history, config):
        self.MarketHistory = market_history
        self.balances = config['backtesting']['initial_balances']
        self.fiat = config['fiat']


    def get_balances (self):
        raise NotImplementedError


    def execute (self,
                 proposed_trades: List[ProposedTrade],
                 market_state: MarketState) -> None:
        raise NotImplementedError


    def get_market_state (self, time: str) -> MarketState:
        # Get the latest chart data from the market
        charts = self.MarketHistory.latest(time)
        balances = self.get_balances()
        # We wrap these data in a MarketState,
        # which provides some convenience methods.
        market_state = MarketState(charts, balances, time, self.fiat)
        return market_state


    def filter_legal (self,
                      proposed_trades: List[ProposedTrade],
                      market_state: MarketState) -> Generator[ProposedTrade, None, None]:
        '''
        Takes a list of ProposedTrade objects.
        Checks that each is a legal trade by the rules of our market.
        '''
        for proposed in proposed_trades:
            if self.is_legal(proposed, market_state):
                yield proposed


    def is_legal (self,
                  proposed: ProposedTrade,
                  market_state: MarketState) -> bool:

        # TODO This is pretty Poloniex specific, so we might move it
        #      to a PoloniexMarketAdapter if we ever add more exchanges.

        # Check that proposed bid has a price:
        if not proposed.price:
            print('WARN: Filtering out proposed trade: trade has no price. Proposed',
                  str(proposed))
            return False

        # Check that we have enough to sell
        if proposed.bid_amount > market_state.balances[proposed.from_coin]:
            print('WARN: Filtering out proposed trade: proposing to sell more than is held. Proposed',
                  str(proposed), 'but holding', market_state.balances[proposed.from_coin], proposed.from_coin)
            return False

        # Check that we are trading a positive amount for a positive amount
        if proposed.bid_amount < 0 or \
           proposed.ask_amount < 0:
            print('WARN: Filtering out proposed trade: bid/ask amounts zero or negative. Proposed',
                  str(proposed))
            return False

        # Check that the proposed trade minimum fiat trade amount.
        if (proposed.from_coin == proposed.fiat and \
            proposed.bid_amount < 0.0001) or \
            (proposed.to_coin == proposed.fiat and \
             proposed.ask_amount < 0.0001):
            print('WARN: Filtering out proposed trade: transaction too small. Proposed',
                  str(proposed))
            return False

        # Check that the trade is on a market that exists.
        if proposed.market_name not in market_state.chart_data.keys():
            print('WARN: Filtering out proposed trade: market name not in chart_data. Proposed',
                  str(proposed))
            return False

        return True
