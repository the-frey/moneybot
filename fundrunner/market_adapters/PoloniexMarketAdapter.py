from . import MarketAdapter

class PoloniexMarketAdapter (MarketAdapter):

    '''
    This adapter just implements an `is_legal` method,
    encoding Poloniex's rules.
    It should apply to any adapter wanting to do business on Poloniex.
    More useful adapters inherit from this.
    '''

    # self, ProposedTrade, MarketState -> Bool
    def is_legal (self, proposed, market_state):

        # Check that proposed bid has a price:
        if not proposed.price:
            print('WARN: Filtering out proposed trade: trade has no price. Proposed',
                  str(proposed))
            return False

        # Check that we have enough to sell
        if proposed.bid_amount > market_state.balances[proposed.from_coin]:
            print('WARN: Filtering out proposed trade: proposing to sell more than is held. Proposed',
                  str(proposed), 'but holding', balances[proposed.from_coin], proposed.from_coin)
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
