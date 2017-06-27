import pandas as pd
from influxdb import InfluxDBClient
from fundrunner.coinstore import HistoricalCoinStore
from . import Purchase
from .balances import Balances

class Strategy (object):
    def __init__ (self, config, #coinstore, initial_balances,
                  market=None, fiat='BTC'):

        self.fiat = fiat

        # Interval between trades, in seconds
        self.trade_interval = config['trade_interval'] 

        # Set up the InfluxDB with historical chart data
        client = InfluxDBClient(config['db']['hostname'],
                                config['db']['port'],
                                config['db']['username'],
                                config['db']['password'],
                                config['db']['database'])

        # If we're backtesting,
        if config['backtesting']['should_backtest']:
            # Set up the historical coinstore
            coinstore = HistoricalCoinStore(client)
            # And get our initial balances
            initial_balances = config['backtesting']['initial_balances']

        # TODO elif config['livetrading']['should-livetrade']
        # constore = .........
        # initial_balances = .........

        self.coinstore = coinstore
        self.initial_balances = initial_balances
        # TODO What is a market? why is it often None?
        self.market = market

    # self, str, str => List<Float>
    def begin_backtest (self, start_time, end_time):
        '''
        Takes a start time and end time (as parse-able date strings).

        Returns a list of USD values for each point (trade interval)
        between start and end.
        '''
        # A series of trade-times to run each of our strategies through.
        dates = pd.date_range(pd.Timestamp(start_time),
                              pd.Timestamp(end_time),
                              freq='{!s}S'.format(self.trade_interval))
        # TODO why is Balances being called down here, not in __init__()?
        self.balances = Balances(dates[0], self.initial_balances)
        for date in dates:
            val = self.step(date)
            yield val

    def step (self, time):
        charts        = self.coinstore.latest_candlesticks(time)
        purchases     = self.get_purchases(charts, self.balances)
        if self.market:
            results   = [self.market.make_purchase(purchase)
                         for purchase in purchases]
        self.balances = self.balances.apply_purchases(time, purchases)
        btc_value     = self.balances.estimate_total_fiat_value(charts)
        usd_btc_price = self.coinstore.btc_price(time)
        usd_value     = btc_value * usd_btc_price
        return round(usd_value, 2)

    # def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    #     raise NotImplementedError

    def set_market(self, market):
        self.market = market
