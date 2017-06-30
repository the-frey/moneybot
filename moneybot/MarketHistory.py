import pandas as pd
from influxdb import InfluxDBClient
from poloniex import Poloniex
import time
from datetime import datetime
from dateutil import parser
from funcy import compose, partial
import requests
import json


def scrape_since_last_reading (client):

    YEAR = 60 * 60 * 24 * 365
    YEAR_AGO = time.time()-YEAR
    polo     = Poloniex()
    strftime = lambda ts: ts.strftime('%Y-%m-%d %H:%M:%S')

    def historical (ticker):
        url =  'https://graphs.coinmarketcap.com/currencies/{!s}'.format(ticker)
        return requests.get(url).json()


    def market_cap (hist_ticker):
        r = {}
        ts = None
        for key, vals in hist_ticker.items():
            if ts is None:
                ts = [pd.to_datetime(t[0]*1000000) for t in vals]
            r[key] = [t[1] for t in vals]
        return pd.DataFrame(r, index=ts)


    coin_history = compose(market_cap, historical)
    btc_price_hist = coin_history('bitcoin')

    # String, PandasSeries -> InfluxMeasurement
    def scraped_chart (currency_pair, row):
        return {
            'measurement': 'scrapedChart',
            'tags': {
                'currencyPair': currency_pair,
            },
            'time': strftime(row.name),
            'fields': row.to_dict(),
        }


    # Str, Int -> PandasSeries
    def historical_prices_of (pair, period=900, start=YEAR_AGO, end=time.time()):
        '''
        Returns a series of time-indexed prices.

        `pair` is of the form e.g. 'BTC_ETH',
        `period` is an integer number of seconds,
        either 300, 900, 1800, 7200, 14400, or 86400.
        '''
        ex_trades = polo.returnChartData(pair,
                                         period,
                                         start, end)
        ts_df = pd.DataFrame(ex_trades, dtype=float)
        ts_df.index = [datetime.fromtimestamp(t)
                       for t in ts_df['date']]
        ts_df = ts_df.drop(['date'], axis=1)
        contemporary_btc_price = lambda row: btc_price_hist['price_usd'].asof(row.name)
        contemporary_usd_price = lambda row: row['weightedAverage']*contemporary_btc_price(row)
        ts_df['price_usd'] = ts_df.apply(contemporary_usd_price, axis=1)
        for _, row in ts_df.iterrows():
            yield scraped_chart(pair, row)


    # get the most recent chart data
    # already fetched from the db
    latest_result = client.query('''
    select * from scrapedChart
    order by time desc
    limit 1
    ''')

    # Get the last time we fetched some data,
    # looking at the most recent result in the db
    latest_fetch_time = parser.parse(
        # sorry this is hack city
        list(latest_result.get_points())[0]['time'])

    # convert from string to unix time
    latest_fetch_unix = time.mktime(
        latest_fetch_time.timetuple())

    # for each market,
    for market in polo.returnTicker():
        # fetch all the chart data
        # since that last fetch.
        try:
            generator = historical_prices_of(market,
                                             start=latest_fetch_unix,
                                             end=time.time())
            client.write_points(generator)
            print('scraped %s', market)
        except:
            print('error scraping %s market', market)


class MarketHistory (object):

    '''
    TODO Docstring
    '''

    def __init__ (self, config):
        self.client = InfluxDBClient(config['db']['hostname'],
                                     config['db']['port'],
                                     config['db']['username'],
                                     config['db']['password'],
                                     config['db']['database'])


    def scrape_latest (self):
        return scrape_since_last_reading(self.client)

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
        group by currencyPair
        order by time desc
        limit 1
        '''.format(time, time)
        result_set = self.client.query(q)
        coin_generator_tuples = { r[0][1]['currencyPair']: list(r[1])[0]
                                 for r in result_set.items() }
        return coin_generator_tuples


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

