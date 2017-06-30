from .PoloniexMarketAdapter import PoloniexMarketAdapter
from poloniex import Poloniex
from time import sleep
import operator

def LiveMarketAdapter (PoloniexMarketAdapter):

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
        for trade in proposed_trades:
            self._place_order(trade, market_state)
        self.balances = self.get_balances()


    '''
    Private methods
    '''

    # Float, Method, [Float] -> Float
    def _adjust (val, operator, tweak = 0.001):
        '''
        Pass in `operator.__add__`
        or `operator.__sub__`
        to move `val` up or down by `tweak`.
        '''
        return operator(val, (val*tweak))


    # TODO Immediate or cancel....then recursive
    #
    #     otherwise too much crazy shit
    #      - orders might be partially fulfilled,
    #      - we don't know which order we're cancelling
    #      - need to do 3 separate API calls before re-placing order
    #     etc..
    #
    # ProposedTrade -> ProposedTrade or None
    def _place_order (self, proposed_trade, market_state):

        # polo.buy
        if proposed_trade.from_coin == market_state.fiat:
            res = self.polo.buy(
                proposed_trade.market_name,
                proposed_trade.market_price,
                proposed_trade.ask_amount
            )

        # polo.sell
        elif proposed_trade.to_coin == market_state.fiat:
            res = self.polo.sell(
                proposed_trade.market_name,
                proposed_trade.market_price,
                proposed_trade.bid_amount
            )

        # # Wait, then see if any orders still open
        # sleep(1)
        # _, coin_pairs = self.cancel_open_orders()
        # # if we canceled some order
        # if coin_pairs is not None:
        #     # Lower bid
        #     if proposed_trade.from_coin == market_state.fiat:
        #         proposed.bi
        #         purchaseList[3] = purchaseList[3] - purchaseList[3] * 0.001
        #     # Increase bid
        #     elif purchaseList[2] == fiat:
        #         purchaseList[1] = purchaseList[1] + purchaseList[1] * 0.001
        #     newPurchase = Purchase(purchaseList[0], purchaseList[1], purchaseList[2], purchaseList[3])
        #     # Recursively make_purchase
        #     return self.make_purchase(newPurchase)

    # # -> List<Int>, List<String>
    # def _open_orders(self):
    #     '''
    #     Private method.
    #     Returns all orders open on Polo,
    #     by order number and by what coin was cancelled.
    #     '''
    #     open_orders = self.polo.returnOpenOrders()
    #     open_order_nums = [v[0]['orderNumber'] for v in open_orders.values() if len(v)]
    #     coins_to_try_again = [coin for coin, v in open_orders.items() if len(v)]
    #     return open_order_nums, coins_to_try_again


    # def _cancel_open_orders(self):
    #     '''
    #     Private method.
    #     Cancels all open orders open on Polo.
    #     '''
    #     open_order_ids, open_order_coins = self.open_orders()
    #     if len(open_order_ids) > 0:
    #         # cancel open orders
    #         print('INFO: canceling orders', open_order_coins)
    #         [self.polo.cancelOrder(order) for order in open_order_ids]
    #         return open_order_ids, open_order_coins
    #     return None, None
