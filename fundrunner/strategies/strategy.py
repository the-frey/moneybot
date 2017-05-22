from .. import Purchase
from ..balances import Balances
from .utils import get_purchase_amounts

class Strategy (object):
    def __init__ (self, coinstore, initial_balances,
                  fiat='BTC'):
        self.fiat = fiat
        self.coinstore = coinstore
        self.initial_balances = initial_balances

    def begin_backtest (self, dates):
        self.balances = Balances(dates[0], self.initial_balances)
        for date in dates:
            val = self.step(date)
            yield val

    def step (self, time):
        charts = self.coinstore.available_coins(time)
        trades = self.get_trades(charts, self.balances)
        purchases = [get_purchase_amounts(charts, trade) for trade in trades]
        self.balances = self.balances.apply_purchases(time, purchases)
        value = self.balances.estimate_total_usd_value(charts)
        return value

    # def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    #     raise NotImplementedError

