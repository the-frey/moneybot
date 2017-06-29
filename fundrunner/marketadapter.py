import pandas as pd

class MarketAdapter (object):

    # def __init__ (self):
        # self.client = influx_client


    # self, ProposedTrade, Charts -> Bool
    def is_legal (self, proposed_trade, charts):

        # Check that we are trading a positive amount for a positive amount
        if proposed.bid_amount < 0 or \
           proposed.ask_amount < 0:
            print('WARN: Filtering out proposed trade: bid/ask amounts zero or negative',
                  str(proposed))
            return False

        # Check that the proposed trade minimum fiat trade amount.
        if (proposed.from_coin == proposed.fiat and \
            proposed.bid_amount < 0.0001) or \
            (proposed.to_coin == proposed.fiat and \
             proposed.ask_amount < 0.0001):
            print('WARN: Filtering out proposed trade: transaction too small',
                  str(proposed))
            return False

        # Check that the trade is on a market that exists.
        if proposed.market_name not in charts.keys():
            print('WARN: Filtering out proposed trade: market name not in charts',
                  str(proposed))
            return False

        return True

    # self, List<ProposedTrade>, Charts -> Generator<ProposedTrade>
    def filter_legal (self, proposed_trades, charts):
        '''
        Takes a list of ProposedTrade objects.
        Checks that each is a legal trade by the rules of our market.
        '''
        for proposed in proposed_trades:
            if is_legal(proposed):
                yield proposed


    # List<ProposedTrade> -> Float
    def execute (self, proposed_trades, charts, balances, time):
        '''
        Executes proposed trades,
        returns value of the fund after all trades have been executed
        in USD.
        '''
        # TODO BALANCES
        balances = balances.apply_purchases(proposed_trades)
        return balances


    # TODO 
# class LiveMarketAdapter (MarketAdapter):

#     def __init__(self, influx_client, market):
#         self.market = market
#         self.client = influx_client

#     # List<ProposedTrade> -> Balances
#     def execute (self, proposed_trades, charts, balances, time):
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
