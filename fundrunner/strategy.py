import pandas as pd
from influxdb import InfluxDBClient
from .proposedtrade import ProposedTrade
from .MarketHistory import MarketHistory
from .marketadapter import MarketAdapter#, LiveMarketAdapter
from .balances import Balances
from datetime import datetime
from time import sleep

'''
Utils
'''




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
        proposed_trades = self.propose_trades(charts, self.balances, time) ####             TODO what data structure(s) can encompass all?
        # The user's propose_trades() method could be returning anything,
        # we don't trust it necessarily. So, we have our MarketAdapter
        # assure that all the trades are legal, by the market's rules.
        # TODO Can the Strategy get access to this sanity checker?
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
    Convenience functions
    '''
    def coin_names (self, market_name):
        coins = market_name.split('_')
        return coins[0], coins[1]


    def available_markets (self, chart_data):
        return set([ k for k in chart_data.keys()
                     if k.startswith(self.fiat) ])


    def available_coins (self, chart_data):
        markets = self.available_markets(chart_data)
        return [ self.coin_names(market)[1]
                 for market in markets ] + [ self.fiat ]


    # TODO This feels like MarketAdapter work
    def held_coins_with_chart_data (self, chart_data, balances,
                                    fiat='BTC'):
        avail_coins = self.available_coins(chart_data)
        # The fiat is always available, so we'll add that to the list as well
        avail_coins  += [fiat]
        return set(balances.held_coins()).intersection(avail_coins)


    '''
    Rebalancing tools
    '''

    def propose_trades_to_fiat (self, coins, ideal_fiat_value_per_coin,
                                chart_data, balances):
        for coin in coins:
            if coin != self.fiat:
                # Sell `coin` for `fiat`,
                # estimating how much `fiat` we should bid
                # (and how much `coin` we should ask for)
                # given the fiat value we want that coin to have after the trade
                proposed = ProposedTrade(coin, self.fiat) \
                           .sell_to_achieve_value_of(ideal_fiat_value_per_coin, balances,
                                                     estimate_price_with=chart_data)
                # if self.MarketAdapter.is_legal(proposed, chart_data):
                yield proposed


    def propose_trades_from_fiat (self, coins, investment_per_coin, chart_data, balances):
        for coin in coins:
            proposed = ProposedTrade(self.fiat, coin) \
                       .set_bid_amount(investment_per_coin,
                                       estimate_price_with=chart_data)
            yield proposed


    def initial_proposed_trades (self, chart_data, balances):
        '''
        "Initial" purchases are from fiat.
        (We assume funds start with only a fiat balance.)
        The resulting proposed trades should result in an equal allocation (of value, in fiat)
        across all "reachable" markets (markets in which the base currency is fiat).
        '''
        available_coins = set(self.available_coins(chart_data)) - set([ self.fiat ])
        fiat_investment_per_coin = balances[self.fiat] / ( len(available_coins) + 1.0 )
        return self.propose_trades_from_fiat(available_coins, fiat_investment_per_coin,
                                        chart_data, balances)


    # TODO IF a method takes chart_data, balances, AND fiat,,,,,,,it probably just needs to take ONE market adapter.......
    def rebalancing_proposed_trades (self, coins_to_rebalance, chart_data, balances):

        avail = self.available_markets(chart_data)
        total_value = balances.estimate_total_fiat_value(chart_data)
        ideal_fiat_value_per_coin = total_value / len(avail) # TODO maybe +1? like above?

        proposed_trades_to_fiat = list(self.propose_trades_to_fiat(coins_to_rebalance,
                                                                   ideal_fiat_value_per_coin,
                                                                   chart_data,
                                                                   balances,))
        # proposed_trades_to_fiat = self.MarketAdapter(proposed_trades_to_fiat)

        # Next, we will simulate actually executing all of these trades
        # Afterward, we'll get some simulated balances
        # TODO apply_purchaess should really be some kind of Simulate or whatever in a market adapter
        est_bals_after_fiat_trades = balances.apply_purchases(proposed_trades_to_fiat)

        if self.fiat in coins_to_rebalance and len(proposed_trades_to_fiat) > 0:
            fiat_after_trades        = est_bals_after_fiat_trades[self.fiat]
            to_redistribute          = fiat_after_trades - ideal_fiat_value_per_coin
            markets_divested_from    = [self.fiat + '_' + proposed.from_coin
                                        for proposed in proposed_trades_to_fiat]
            markets_to_buy           = set(avail) - set(markets_divested_from)
            coins_to_buy             = [self.coin_names(m)[1] for m in markets_to_buy]
            to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
            proposed_trades_from_fiat = self.propose_trades_from_fiat(coins_to_buy,
                                                                      to_redistribute_per_coin,
                                                                      chart_data,
                                                                      balances)
            trades = proposed_trades_to_fiat + list(proposed_trades_from_fiat)

            return trades

        return proposed_trades_to_fiat
