import pandas as pd
from influxdb import InfluxDBClient

class MarketHistory (object):

    def __init__ (self, config):
        self.client = InfluxDBClient(config['db']['hostname'],
                                     config['db']['port'],
                                     config['db']['username'],
                                     config['db']['password'],
                                     config['db']['database'])


    # String -> { 'BTC_ETH': { weightedAverage, ...} ...}
    # see https://bitbucket.org/peakrider/poloniex-chart-history
    # TODO One issue here is that we are *only* getting the latest (15-minute) candlestic
    # So, if we are only trading once per day, certain values (like volume) will be misleading,
    # as they won't cover teh whole 24-hour period.
    # We could, in the future, address this by taking all the candlesticks since we last checked
    # and pass them through to the strategy together, sorted ny time.
    # Then, the strategy can then decide how to combine them.
    def latest (self, time):
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
    def btc_rate (self, time,
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
    def usd_value (self, market_state):
        btc_value     = market_state.estimate_total_value()
        btc_usd_rate  = self.btc_rate(market_state.time)
        usd_value     = btc_value * btc_usd_rate
        return round(usd_value, 2)


    # String, String -> [ Float... ]
    def asset_history (self, time, base, quote,
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

