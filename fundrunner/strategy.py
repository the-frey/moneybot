import pandas as pd
from influxdb import InfluxDBClient
from .ProposedTrade import ProposedTrade
from .MarketHistory import MarketHistory
from .MarketAdapter import MarketAdapter#, LiveMarketAdapter
from .MarketState import MarketState
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


    def step (self, time):
        # Get the latest chart data from the market
        charts = self.MarketHistory.latest(time)
        # Now, propose trades. If you're writing a strategy, you will override this method.
        # TODO self.balances is coming out of nowhere.
        #      Can't it get passed into `step()`?
        market_state = MarketState(charts, self.balances, time, self.fiat)
        proposed_trades = self.propose_trades(market_state)
        # Finally, the MarketAdapter will execute our trades.
        # If we're backtesting, these trades won't really happen.
        # If we're trading for real, we will attempt to execute the proposed trades
        # at the best price we can.
        # In either case, the method returns the balances of all assets,
        # and the USD value of our whole fund,
        # after all trades have been executed
        self.balances = self.MarketAdapter.execute(proposed_trades, market_state)
        # # TODO MarketHistory and Balances are tightly coupled here
        usd_value = self.MarketHistory.usd_value(market_state)
        return usd_value


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


    '''
    Rebalancing tools
    '''

    def initial_proposed_trades (self, market_state):
        '''
        "Initial" purchases are from fiat.
        (We assume funds start with only a fiat balance.)
        The resulting proposed trades should result in an equal allocation (of value, in fiat)
        across all "reachable" markets (markets in which the base currency is fiat).
        '''
        available_coins = market_state.available_coins() - set([ self.fiat ])
        fiat_investment_per_coin = market_state.balances[self.fiat] / ( len(available_coins) + 1.0 )
        trades = self.propose_trades_from_fiat(available_coins, fiat_investment_per_coin, market_state)
        return trades


    def propose_trades_to_fiat (self, coins, ideal_fiat_value_per_coin, market_state):
        for coin in coins:
            if coin != self.fiat:
                # Sell `coin` for `fiat`,
                # estimating how much `fiat` we should bid
                # (and how much `coin` we should ask for)
                # given the fiat value we want that coin to have after the trade
                proposed = ProposedTrade(coin, self.fiat) \
                           .sell_to_achieve_value_of(ideal_fiat_value_per_coin, market_state)
                if proposed:
                    yield proposed


    def propose_trades_from_fiat (self, coins, investment_per_coin, market_state):
        for coin in coins:
            proposed = ProposedTrade(self.fiat, coin) \
                       .set_bid_amount(investment_per_coin, market_state)
            yield proposed


    def rebalancing_proposed_trades (self, coins_to_rebalance, market_state):

        available_coins = market_state.available_coins() - set([ self.fiat ])
        total_value = market_state.estimate_total_value() 
        ideal_fiat_value_per_coin = total_value / len(available_coins) # TODO maybe +1? like above?

        proposed_trades_to_fiat = list(self.propose_trades_to_fiat(coins_to_rebalance,
                                                                   ideal_fiat_value_per_coin,
                                                                   market_state,))

        # Next, we will simulate actually executing all of these trades
        # Afterward, we'll get some simulated balances
        # TODO apply_purchaess should really be some kind of Simulate or whatever in a market adapter
        est_bals_after_fiat_trades = market_state.balances.apply_purchases(proposed_trades_to_fiat)

        if self.fiat in coins_to_rebalance and len(proposed_trades_to_fiat) > 0:
            fiat_after_trades        = est_bals_after_fiat_trades[self.fiat]
            to_redistribute          = fiat_after_trades - ideal_fiat_value_per_coin
            coins_divested_from      = [ proposed.from_coin for proposed in proposed_trades_to_fiat]
            coins_to_buy             = available_coins - set(coins_divested_from) - set( [self.fiat] )
            to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
            proposed_trades_from_fiat = self.propose_trades_from_fiat(coins_to_buy, to_redistribute_per_coin, market_state)
            trades = proposed_trades_to_fiat + list(proposed_trades_from_fiat)

            return trades

        return proposed_trades_to_fiat
