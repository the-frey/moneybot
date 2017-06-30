import pandas as pd

class MarketAdapter (object):


    def __init__ (self, config):
        self.balances = config['backtesting']['initial_balances']


    def get_balances (self):
        return self.balances

    # self, ProposedTrade, MarketState -> Bool
    def is_legal (self, proposed, market_state):

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

    # self, List<ProposedTrade>, MarketState -> Generator<ProposedTrade>
    def filter_legal (self, proposed_trades, market_state):
        '''
        Takes a list of ProposedTrade objects.
        Checks that each is a legal trade by the rules of our market.
        '''
        for proposed in proposed_trades:
            if self.is_legal(proposed, market_state):
                yield proposed


    # List<ProposedTrade> -> Float
    def execute (self, proposed_trades, market_state):
        '''
        Executes proposed trades,
        returns value of the fund after all trades have been executed
        in USD.
        '''
        # The user's propose_trades() method could be returning anything,
        # we don't trust it necessarily. So, we have our MarketAdapter
        # assure that all the trades are legal, by the market's rules.
        # TODO Can the Strategy get access to this sanity checker?
        legal_trades = self.filter_legal(proposed_trades, market_state)
        # Now, we will actually execute the trades.
        balances = market_state.simulate_trades(legal_trades)
        self.balances = balances


    # TODO 
# class LiveMarketAdapter (MarketAdapter):

#     def __init__(self, influx_client, market):
#         self.market = market
#         self.client = influx_client

#     # List<ProposedTrade> -> Balances
#     def execute (self, proposed_trades, chart_data, balances, time):
#         # TODO Record proposed + executed trades? OR does tha thappen in market.make_purchase?
#         # TODO executed return type?
#         executed = [self.market.make_purchase(proposed)
#                     for proposed in proposed_trades]
#         # TODO Return type here? Should we apply balances given trades that occured?
#         return executed

#     def latest_chart_data(self, time=''):
#         return self.market.latest_chart_data()

#     def btc_price (self, time=''):
#         rate = requests.get('https://api.gemini.com/v1/pubticker/btcusd').json()
#         return (float(rate['bid'])+float(rate['ask']))/2
