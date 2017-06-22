import pandas as pd
import requests

class HistoricalCoinStore(object):
    def __init__(self, influx_client):

        self.client = influx_client

    # String -> { 'BTC_ETH': { weightedAverage, ...} ...}
    # see https://bitbucket.org/peakrider/poloniex-chart-history
    # TODO One issue here is that we are *only* getting the latest (15-minute) candlestic
    # So, if we are only trading once per day, certain values (like volume) will be misleading,
    # as they won't cover teh whole 24-hour period.
    # We could, in the future, address this by taking all the candlesticks since we last checked
    # and pass them through to the strategy together, sorted ny time.
    # Then, the strategy can then decide how to combine them.
    def latest_candlesticks (self, time):
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
    def btc_price (self, time,
                   key='weightedAverage'):
        q ='''
        select * from scrapedChart
        where time <= '{!s}' and time > '{!s}' - 30d
        and currencyPair = 'USD_BTC'
        order by time desc
        limit 1
        '''.format(time, time)
        result_set = self.client.query(q)
        return list(result_set.get_points())[-1][key]

    # String, String -> [ Float... ]
    def market_history (self, currency_pair, time,
                            days_back=30, key='weightedAverage'):
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

class LiveCoinStore(object):
    def __init__(self, market):
        self.market = market

    def latest_candlesticks(self, time=''):
        return self.market.latest_chart_data()

    def btc_price (self, time=''):
        rate = requests.get('https://api.gemini.com/v1/pubticker/btcusd').json()
        return (float(rate['bid'])+float(rate['ask']))/2
