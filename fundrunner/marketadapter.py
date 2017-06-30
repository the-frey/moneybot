import pandas as pd

class MarketAdapter (object):


    def get_balances (self):
        raise NotImplementedError


    def execute (self, proposed_trades, market_state):
        raise NotImplementedError


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


    # self, List<ProposedTrade>, MarketState -> Generator<ProposedTrade>
    def filter_legal (self, proposed_trades, market_state):
        '''
        Takes a list of ProposedTrade objects.
        Checks that each is a legal trade by the rules of our market.
        '''
        for proposed in proposed_trades:
            if self.is_legal(proposed, market_state):
                yield proposed


class BacktestMarketAdapter (MarketAdapter):

    def __init__ (self, config):
        self.balances = config['backtesting']['initial_balances']


    def get_balances (self):
        return self.balances


    def execute (self, proposed_trades, market_state):
        # Now, we will actually execute the trades.
        balances = market_state.simulate_trades(proposed_trades)
        self.balances = balances



from poloniex import Poloniex
from time import sleep
def LiveMarketAdapter (MarketAdapter):

    def __init__ (self, config):
        self.polo = Poloniex(self.config['livetrading']['poloniex']['pk'],
                             self.config['livetrading']['poloniex']['sk'])
        self.balances = self.get_balances()


    def get_balances (self):
        bals = self.polo.returnCompleteBalances()
        all_balances = {}
        for coin, bal, in bals.items():
            avail = float(bal['available'])
            if  avail > 0:
                all_balances[coin] = avail
        return all_balances


    def execute (self, proposed_trades, market_state):
        # Now, we will actually execute the trades.
        balances = market_state.simulate_trades(proposed_trades)
        self.balances = self.get_balances()


    '''
    Private methods
    '''

    # ProposedTrade -> ProposedTrade or None
    def make_purchase(self, proposed_trade, market_state):

        # TODO polo.sell
        if proposed_trade.from_coin == market_state.fiat:
            res = self.polo.buy(
                proposed_trade.market_name,
                proposed_trade.price,
                proposed_trade.ask_amount
                )
        proposed_trade.market_name

        if not purchase:
            return None
        if purchase.from_coin == fiat:
            market = fiat + "_" + purchase.to_coin
            rate = purchase.from_amount / purchase.to_amount
            print("BUY", market, purchase.to_amount)
            # market, (FIAT / OTHER), OTHER
            res = self.polo.buy(market, rate, purchase.to_amount)
        elif purchase.to_coin == fiat:
            market = fiat + "_" + purchase.from_coin
            rate = purchase.to_amount / purchase.from_amount
            print("SELL", market, purchase.to_amount)
            # market, (FIAT / OTHER), OTHER
            res = self.polo.sell(market, rate, purchase.from_amount)
            # Wait, then see if any orders still open
        sleep(1)
        _, coin_pairs = self.cancel_open_orders()
        # if we canceled some order
        if coin_pairs is not None:
            for coin_pair in coin_pairs:
                purchaseList = list(purchase)
                # Lower bid
                if purchaseList[0] == fiat:
                    purchaseList[3] = purchaseList[3] - purchaseList[3] * 0.001
                # Increase bid
                elif purchaseList[2] == fiat:
                    purchaseList[1] = purchaseList[1] + purchaseList[1] * 0.001
                newPurchase = Purchase(purchaseList[0], purchaseList[1], purchaseList[2], purchaseList[3])
                # Recursively make_purchase
                return self.make_purchase(newPurchase)

    # -> List<Int>, List<String>
    def _open_orders(self):
        '''
        Private method.
        Returns all orders open on Polo,
        by order number and by what coin was cancelled.
        '''
        open_orders = self.polo.returnOpenOrders()
        open_order_nums = [v[0]['orderNumber'] for v in open_orders.values() if len(v)]
        coins_to_try_again = [coin for coin, v in open_orders.items() if len(v)]
        return open_order_nums, coins_to_try_again


    def _cancel_open_orders(self):
        '''
        Private method.
        Cancels all open orders open on Polo.
        '''
        open_order_ids, open_order_coins = self.open_orders()
        if len(open_order_ids) > 0:
            # cancel open orders
            print('INFO: canceling orders', open_order_coins)
            [self.polo.cancelOrder(order) for order in open_order_ids]
            return open_order_ids, open_order_coins
        return None, None




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
