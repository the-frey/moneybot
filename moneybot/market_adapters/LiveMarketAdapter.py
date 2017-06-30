from . import MarketAdapter
from poloniex import Poloniex
from time import sleep
import operator

class LiveMarketAdapter (MarketAdapter):

    def __init__ (self, config):
        self.polo = Poloniex(config['livetrading']['poloniex']['pk'],
                             config['livetrading']['poloniex']['sk'])
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


    # Float -> Float
    def _adjust_up (self, val, **kwargs):
        return _adjust(val, operator.__add__, **kwargs)


    # Float -> Float
    def _adjust_down (self, val, **kwargs):
        return _adjust(val, operator.__sub__, **kwargs)


    def _purchase_helper (self, market, price, amount, purchase_fn, adjust_fn):
        try:
            res = purchase_fn(
                market,
                price,
                amount,
                # Cancel order if not fulfilled in entirity at this price
                orderType = 'fillOrKill')
        # If we can't fill the order at this price,
        except:
            # recursively again at a (higher / lower) price
            return _purchase_helper(
                market,
                adjust_fn(price),
                amount,
                purchase_fn,
                adjust_fn
            )
        return res


    # ProposedTrade -> Response
    def _place_order (proposed_trade, market_state):

        # if we're trading FROM fiat, that's a "sell"
        if proposed_trade.from_coin == market_state.fiat:
            return _purchase_helper(
                proposed_trade.market_name,
                proposed_trade.market_price,
                proposed_trade.ask_amount,
                polo.buy,
                # We try to buy low,
                # But don't always get to,
                # so we adjust up if we must.
                _adjust_up,
            )

        # if we're trading TO fiat, that's a "sell"
        elif proposed_trade.to_coin == market_state.fiat:
            return _purchase_helper(
                proposed_trade.market_name,
                proposed_trade.market_price,
                proposed_trade.ask_amount,
                polo.sell,
                # We try to sell high,
                # But don't always get to,
                # so we adjust down if we must.
                _adjust_down,
            )
