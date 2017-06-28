import pandas as pd

class MarketAdapter (object):

    def __init__ (self, influx_client):
        self.client = influx_client


    # List<ProposedTrade> -> Generator<ProposedTrade>
    def filter_legal (self, proposed_trades, charts):
        '''
        Takes a list of ProposedTrade objects.
        Checks that each is a legal trade by the rules of our market.
        '''
        for proposed in proposed_trades:
            # Check that we are trading a positive amount for a positive amount
            if proposed.bid_amount < 0 or \
                 proposed.ask_amount < 0:
                print('WARN: Filtering out proposed trade: bid/ask amounts zero or negative',
                      str(proposed))
                continue
            # Check that the proposed trade minimum fiat trade amount.
            if (proposed.from_coin == proposed.fiat and \
                proposed.bid_amount < 0.0001) or \
               (proposed.to_coin == proposed.fiat and \
                proposed.ask_amount < 0.0001):
                print('WARN: Filtering out proposed trade: transaction too small',
                      str(proposed))
                continue
            # Check that the trade is on a market that exists.
            if proposed.market_name not in charts.keys():
                print('WARN: Filtering out proposed trade: market name not in charts',
                      str(proposed))
                continue

            # if all these tests pass,
            # the proposed trade is legal!
            yield proposed


    # List<ProposedTrade> -> Float
    def execute (self, proposed_trades, charts, balances, time):
        '''
        Executes proposed trades,
        returns value of the fund after all trades have been executed
        in USD.
        '''
        # TODO BALANCES
        balances = balances.apply_purchases(proposed_trades)
        return balances


    # String -> { 'BTC_ETH': { weightedAverage, ...} ...}
    # see https://bitbucket.org/peakrider/poloniex-chart-history
    # TODO One issue here is that we are *only* getting the latest (15-minute) candlestic
    # So, if we are only trading once per day, certain values (like volume) will be misleading,
    # as they won't cover teh whole 24-hour period.
    # We could, in the future, address this by taking all the candlesticks since we last checked
    # and pass them through to the strategy together, sorted ny time.
    # Then, the strategy can then decide how to combine them.
    def latest_chart_data (self, time):
        q ='''
        select * from scrapedChart
        where time <= '{!s}' and time > '{!s}' - 1d
        and currencyPair != 'USD_BTC'
        group by currencyPair
        order by time desc
        limit 1
        '''.format(time, time)
        result_set = self.client.query(q)
        coin_generator_tuples = { r[0][1]['currencyPair']: list(r[1])[0]
                                 for r in result_set.items() }
        return coin_generator_tuples


    # String -> Float
    def btc_rate(self, time,
                 key='weightedAverage'):
        '''
        Returns the rate of BTC in USD.
        '''
        q ='''
        select * from scrapedChart
        where time <= '{!s}' and time > '{!s}' - 30d
        and currencyPair = 'USD_BTC'
        order by time desc
        limit 1
        '''.format(time, time)
        result_set = self.client.query(q)
        return list(result_set.get_points())[-1][key]


    # PandasTimestamp, Balances, Charts -> Float
    def usd_value (self, time, balances, charts):
        btc_value     = balances.estimate_total_fiat_value(charts)
        btc_usd_rate  = self.btc_rate(time)
        usd_value     = btc_value * btc_usd_rate
        return round(usd_value, 2)


    # String, String -> [ Float... ]
    def market_history (self, base, quote, time,
                            days_back=30, key='price_usd'):
        currency_pair = '{!s}_{!s}'.format(base, quote)
        q ='''
        select * from scrapedChart
        where currencyPair='{!s}'
        and time <= '{!s}' and time > '{!s}' - {!s}d
        order by time desc
        '''.format(currency_pair, time, time, days_back)
        result_set = self.client.query(q)
        prices     = [(p['time'], p[key]) for p in result_set.get_points()]
        df = pd.Series([p[1] for p in prices])
        df.index = [p[0] for p in prices]
        return df




class LiveMarketAdapter (MarketAdapter):

    def __init__(self, influx_client, market):
        self.market = market
        self.client = influx_client

    # List<ProposedTrade> -> Balances
    def execute (self, proposed_trades, charts, balances, time):
        # TODO Record proposed + executed trades? OR does tha thappen in market.make_purchase?
        # TODO executed return type?
        executed = [self.market.make_purchase(proposed)
                    for proposed in proposed_trades]
        # TODO Return type here? Should we apply balances given trades that occured?
        return executed

    def latest_chart_data(self, time=''):
        return self.market.latest_chart_data()

    def btc_price (self, time=''):
        rate = requests.get('https://api.gemini.com/v1/pubticker/btcusd').json()
        return (float(rate['bid'])+float(rate['ask']))/2
