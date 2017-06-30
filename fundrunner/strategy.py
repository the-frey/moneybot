from .ProposedTrade import ProposedTrade
from .MarketHistory import MarketHistory
from .MarketState import MarketState
from datetime import datetime
from time import sleep
import pandas as pd


class Strategy (object):

    '''
    TODO Docstring
    '''

    def __init__ (self, MarketAdapter, config,
                  fiat='BTC'):
        self.config = config
        self.fiat = fiat
        # MarketHistory stores historical market data
        self.MarketHistory = MarketHistory(self.config)
        # Interval between trades, in seconds
        self.trade_interval = config['trade_interval']
        # This is set internally at runtime
        # TODO Better place for this? Where to pass this in?
        self.MarketAdapter = MarketAdapter(self.config)


    def step (self, time):
        # Get the latest chart data from the market
        charts = self.MarketHistory.latest(time)
        balances = self.MarketAdapter.get_balances()
        # We wrap these data in a MarketState,
        # which provides some convenience methods.
        market_state = MarketState(charts, balances, time, self.fiat)
        # Now, propose trades. If you're writing a strategy, you will override this method.
        proposed_trades = self.propose_trades(market_state)
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

    # MarketState -> Set<Str>
    def _possible_investments (self, market_state):
        '''
        Returns a set of all coins that the strategy might invest in,
        not including the fiat.
        '''
        return market_state.available_coins() - set([ self.fiat ])


    # Seq<str>, Float, MarketState -> Generator<ProposedTrade>
    def _propose_trades_to_fiat (self, coins, fiat_value_per_coin, market_state):
        for coin in coins:
            if coin != self.fiat:
                # Sell `coin` for `fiat`,
                # estimating how much `fiat` we should bid
                # (and how much `coin` we should ask for)
                # given the fiat value we want that coin to have after the trade
                proposed = ProposedTrade(coin, self.fiat) \
                           .sell_to_achieve_value_of(fiat_value_per_coin, market_state)
                if proposed:
                    yield proposed


    # Seq<str>, Float, MarketState -> Generator<ProposedTrade>
    def _propose_trades_from_fiat (self, coins, fiat_investment_per_coin, market_state):
        for coin in coins:
            proposed = ProposedTrade(self.fiat, coin) \
                       .set_bid_amount(fiat_investment_per_coin, market_state)
            yield proposed


    def initial_proposed_trades (self, market_state):
        '''
        "Initial" purchases are from fiat.
        (We assume funds start with only a fiat balance.)
        The resulting proposed trades should result in an equal allocation (of value, in fiat)
        across all "reachable" markets (markets in which the base currency is fiat).
        '''
        possible_investments = self._possible_investments(market_state)
        fiat_investment_per_coin = market_state.balances[self.fiat] / ( len(possible_investments) + 1.0 )
        trades = self._propose_trades_from_fiat(possible_investments,
                                                fiat_investment_per_coin,
                                                market_state)
        return trades



    def rebalancing_proposed_trades (self, coins_to_rebalance, market_state):

        possible_investments = self._possible_investments(market_state)
        total_value = market_state.estimate_total_value()
        ideal_fiat_value_per_coin = total_value / len(possible_investments)

        proposed_trades_to_fiat = list(self._propose_trades_to_fiat(coins_to_rebalance,
                                                                    ideal_fiat_value_per_coin,
                                                                    market_state))

        # Next, we will simulate actually executing all of these trades
        # Afterward, we'll get some simulated balances
        est_bals_after_fiat_trades = market_state.simulate_trades(proposed_trades_to_fiat)

        if self.fiat in coins_to_rebalance and len(proposed_trades_to_fiat) > 0:
            fiat_after_trades        = est_bals_after_fiat_trades[self.fiat]
            to_redistribute          = fiat_after_trades - ideal_fiat_value_per_coin
            coins_divested_from      = [ proposed.from_coin for proposed in proposed_trades_to_fiat]
            coins_to_buy             = possible_investments - set(coins_divested_from) - set( [self.fiat] )
            to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
            proposed_trades_from_fiat = self._propose_trades_from_fiat(coins_to_buy,
                                                                       to_redistribute_per_coin,
                                                                       market_state)
            trades = proposed_trades_to_fiat + list(proposed_trades_from_fiat)

            return trades

        return proposed_trades_to_fiat
