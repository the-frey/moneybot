import pandas as pd
from influxdb import InfluxDBClient
from fundrunner.coinstore import HistoricalCoinStore
from . import Purchase
from .balances import Balances

class Strategy (object):
    def __init__ (self, config, 
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
            self.coinstore = HistoricalCoinStore(client)
            # And get our initial balances
            initial_balances = config['backtesting']['initial_balances']
            self.balances = Balances(initial_balances)

        elif config['live_trading']['should_livetrade']:
            self.market = PoloniexMarket(config['poloniex']['pk'],
                                         config['poloniex']['sk'])
            self.coinstore = LiveCoinStore(client, market)
            initial_balances = market.get_balances()
            self.balances = Balances(initial_balances)

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
        for date in dates:
            val = self.step(date)
            yield val

    def step (self, time):
        charts        = self.coinstore.latest_candlesticks(time)
        purchases     = self.get_purchases(charts, self.balances)
        if self.market:
            results   = [self.market.make_purchase(purchase)
                         for purchase in purchases]
        self.balances = self.balances.apply_purchases(purchases)
        btc_value     = self.balances.estimate_total_fiat_value(charts)
        usd_btc_price = self.coinstore.btc_price(time)
        usd_value     = btc_value * usd_btc_price
        return round(usd_value, 2)

    # def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    #     raise NotImplementedError
