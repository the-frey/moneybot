from .MarketHistory import MarketHistory
from .MarketState import MarketState
from datetime import datetime
from time import sleep
import pandas as pd


class Fund (object):

    '''
    TODO Docstring
    '''

    def __init__ (self, Strategy, MarketAdapter, config):
        self.config = config
        self.Strategy = Strategy(self.config)
        # MarketHistory stores historical market data
        self.MarketHistory = MarketHistory(self.config)
        # MarketAdapter executes trades, fetches balances
        self.MarketAdapter = MarketAdapter(self.config)


    def step (self, time):
        # Get the latest chart data from the market
        charts = self.MarketHistory.latest(time)
        balances = self.MarketAdapter.get_balances()
        # We wrap these data in a MarketState,
        # which provides some convenience methods.
        market_state = MarketState(charts, balances, time, self.Strategy.fiat)
        # Now, propose trades. If you're writing a strategy, you will override this method.
        proposed_trades = self.Strategy.propose_trades(market_state, self.MarketHistory)
        # If the strategy proposed any trades, we execute them.
        if proposed_trades:
            # The user's propose_trades() method could be returning anything,
            # we don't trust it necessarily. So, we have our MarketAdapter
            # assure that all the trades are legal, by the market's rules.
            # `filter_legal()` will throw informative warnings if any trades
            # get filtered out!
            # TODO Can the Strategy get access to this sanity checker?
            assumed_legal_trades = self.MarketAdapter.filter_legal(proposed_trades, market_state)
            # Finally, the MarketAdapter will execute our trades.
            # If we're backtesting, these trades won't really happen.
            # If we're trading for real, we will attempt to execute the proposed trades
            # at the best price we can.
            # In either case, this method is side-effect-y;
            # it sets MarketAdapter.balances, after all trades have been executed.
            self.MarketAdapter.execute(assumed_legal_trades, market_state)
        # Finally, we get the USD value of our whole fund,
        # now that all trades (if there were any) have been executed.
        usd_value = market_state.estimate_total_value_usd()
        return usd_value


    def run_live (self):
        while True:
            # TODO Backfill historical data using the scraper!
            cur_time = datetime.now()
            print('Trading', cur_time)
            usd_val = self.step(cur_time)
            print('Est. USD value', usd_val)
            # TODO Count the time that the step took to run
            #      see poloniex-index-fund-bot for how this is done
            sleep(self.Strategy.trade_interval)


    # self, str, str => List<Float>
    def begin_backtest (self, start_time, end_time):
        '''
        Takes a start time and end time (as parse-able date strings).

        Returns a list of USD values for each point (trade interval)
        between start and end.
        '''
        # MarketAdapter executes trades
        # Set up the historical coinstore
        # A series of trade-times to run each of our strategies through.
        dates = pd.date_range(pd.Timestamp(start_time),
                              pd.Timestamp(end_time),
                              freq='{!s}S'.format(self.Strategy.trade_interval))
        for date in dates:
            val = self.step(date)
            yield val
