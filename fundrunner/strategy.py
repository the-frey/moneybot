import pandas as pd
from influxdb import InfluxDBClient
from fundrunner.coinstore import HistoricalCoinStore, LiveCoinStore
from .balances import Balances
from .market import PoloniexMarket
from datetime import datetime
from time import sleep

class Strategy (object):
    def __init__ (self, config,
                  market=None, fiat='BTC'):

        self.config = config

        self.trade_interval = config['trade_interval']

        self.fiat = fiat

        # Interval between trades, in seconds
        self.trade_interval = config['trade_interval']

        # Set up the InfluxDB with historical chart data
        self.client = InfluxDBClient(config['db']['hostname'],
                                     config['db']['port'],
                                     config['db']['username'],
                                     config['db']['password'],
                                     config['db']['database'])

        # This is none until initialize (until run_live() is called)
        self.market = None

    def run_live (self):
        self.market = PoloniexMarket(self.config['livetrading']['poloniex']['pk'],
                                     self.config['livetrading']['poloniex']['sk'])
        self.coinstore = LiveCoinStore(self.client, self.market)
        initial_balances = self.market.get_balances()
        self.balances = Balances(initial_balances)
        while True:
            cur_time = datetime.now()
            print('Trading', cur_time)
            usd_val = self.step(cur_time)
            print('Est. USD value', usd_val)
            # TODO Count the time that the step took to run
            #      see poloniex-index-fund-bot for how this is done
            sleep(self.trade_interval)

    # self, str, str => List<Float>
    def begin_backtest (self, start_time, end_time):
        '''
        Takes a start time and end time (as parse-able date strings).

        Returns a list of USD values for each point (trade interval)
        between start and end.
        '''
        # Set up the historical coinstore
        self.coinstore = HistoricalCoinStore(self.client)
        # And get our initial balances
        initial_balances = self.config['backtesting']['initial_balances']
        self.balances = Balances(initial_balances)
        # A series of trade-times to run each of our strategies through.
        dates = pd.date_range(pd.Timestamp(start_time),
                              pd.Timestamp(end_time),
                              freq='{!s}S'.format(self.trade_interval))
        for date in dates:
            val = self.step(date)
            yield val

    def step (self, time):
        charts          = self.coinstore.latest_candlesticks(time)
        proposed_trades = self.propose_trades(charts, self.balances, time)
        if self.market:
            # TODO PURCHASE
            #      this can execute asks,
            #      return trades
            #      remember - in the future, will all go into InfluxDB
            results   = [self.market.make_purchase(proposed)
                         for proposed in proposed_trades]
        # TODO BALANCES
        #      apply_balances is a monolith
        #      it's also really more of a simulate_purchases we use in backtesting.
        #      we could split the logic up, to sanity check trade proposals.
        self.balances = self.balances.apply_purchases(proposed_trades)
        # TODO The rest here are impl details, can be hidden in a market adapter!
        btc_value     = self.balances.estimate_total_fiat_value(charts)
        usd_btc_price = self.coinstore.btc_price(time)
        usd_value     = btc_value * usd_btc_price
        return round(usd_value, 2)
