import pandas as pd
from influxdb import InfluxDBClient
# from fundrunner.coinstore import HistoricalCoinStore, LiveCoinStore
# from .market import PoloniexMarket
from .MarketHistory import MarketHistory
from .marketadapter import MarketAdapter#, LiveMarketAdapter
from .balances import Balances
from datetime import datetime
from time import sleep

class Strategy (object):


    def __init__ (self, config,
                  market=None, fiat='BTC'):
        self.config = config
        self.fiat = fiat
        # MarketHistory stores historical market data
        self.MarketHistory = MarketHistory(self.config)
        # Interval between trades, in seconds
        self.trade_interval = config['trade_interval']
        # This is set internally at runtime
        # TODO Better place for this? Where to pass this in?
        self.MarketAdapter = None



    def run_live (self):
        # TODO 
        # self.market = PoloniexMarket(self.config['livetrading']['poloniex']['pk'],
        #                              self.config['livetrading']['poloniex']['sk'])
        # TODO self.coinstore = LiveCoinStore(self.client, self.market)
        initial_balances = self.market.get_balances()
        # TODO Does Balances need to be here?
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
        # MarketAdapter executes trades
        # Set up the historical coinstore
        self.MarketAdapter = MarketAdapter()
        # And get our initial balances
        initial_balances = self.config['backtesting']['initial_balances']
        # TODO Does Balances need to be here?
        self.balances = Balances(initial_balances)
        # A series of trade-times to run each of our strategies through.
        dates = pd.date_range(pd.Timestamp(start_time),
                              pd.Timestamp(end_time),
                              freq='{!s}S'.format(self.trade_interval))
        for date in dates:
            val = self.step(date)
            yield val


    def step (self, time):
        # Get the latest chart data from the market
        charts = self.MarketHistory.latest_chart_data(time)
        # Now, propose trades. If you're writing a strategy, you will override this method.
        # TODO self.balances is coming out of nowhere.
        #      Can't it get passed into `step()`?
        proposed_trades = self.propose_trades(charts, self.balances, time)
        # The user's propose_trades() method could be returning anything,
        # we don't trust it necessarily. So, we have our MarketAdapter
        # assure that all the trades are legal, by the market's rules.
        legal_trades = self.MarketAdapter.filter_legal(proposed_trades, charts)
        # Finally, the MarketAdapter will execute our trades.
        # If we're backtesting, these trades won't really happen.
        # If we're trading for real, we will attempt to execute the proposed trades
        # at the best price we can.
        # In either case, the method returns the balances of all assets,
        # and the USD value of our whole fund,
        # after all trades have been executed
        self.balances = self.MarketAdapter.execute(legal_trades, charts, self.balances, time)
        # # TODO MarketHistory and Balances are tightly coupled here
        usd_value = self.MarketHistory.usd_value(time, self.balances, charts)
        return usd_value
