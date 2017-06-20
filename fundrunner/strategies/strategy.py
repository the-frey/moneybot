from .. import Purchase
from ..balances import Balances
from .utils import get_purchases

class Strategy (object):
    def __init__ (self, coinstore, initial_balances,
                  market=None, fiat='BTC'):
        self.fiat = fiat
        self.coinstore = coinstore
        self.initial_balances = initial_balances
        self.market = market

    def begin_backtest (self, dates):
        self.balances = Balances(dates[0], self.initial_balances)
        for date in dates:
            val = self.step(date)
            yield val

    def step (self, time):
        charts        = self.coinstore.latest_candlesticks(time)
        trades        = self.get_trades(charts, self.balances)
        purchases     = [get_purchases(charts, trade) for trade in trades]
        if self.market:
            results   = [self.market.make_purchase(purchase) for purchase in purchases]
        self.balances = self.balances.apply_purchases(time, purchases)
        btc_value     = self.balances.estimate_total_fiat_value(charts)
        usd_btc_price = self.coinstore.btc_price(time)
        usd_value     = btc_value * usd_btc_price
        return usd_value

    # def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    #     raise NotImplementedError

    def set_market(self, market):
        self.market = market
