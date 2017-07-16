# -*- coding: utf-8 -*-
import time
from datetime import datetime
from datetime import timedelta
from dateutil import parser
from logging import getLogger
from typing import Dict
from typing import List
from typing import Optional

import requests
from funcy import compose
# TODO this should be postgresified
from influxdb import InfluxDBClient
from pandas import DataFrame
from pandas import Series
from pandas import to_datetime

from moneybot.clients import Postgres
from moneybot.clients import Poloniex


YEAR_IN_SECS = 60 * 60 * 24 * 365

logger = getLogger(__name__)


def format_time(ts: datetime) -> str:
    return ts.strftime('%Y-%m-%d %H:%M:%S')


# TODO This should be postgresified
def scrape_since_last_reading(client: InfluxDBClient):
    polo = Poloniex.get_client()

    def historical(ticker: str) -> Dict:
        url = f'https://graphs.coinmarketcap.com/currencies/{ticker}'
        return requests.get(url).json()

    def market_cap(hist_ticker: Dict) -> Series:
        r = {}
        ts = None
        for key, vals in hist_ticker.items():
            if ts is None:
                ts = [to_datetime(t[0] * 1000000) for t in vals]
            r[key] = [t[1] for t in vals]
        return DataFrame(r, index=ts)

    coin_history = compose(market_cap, historical)
    btc_price_hist = coin_history('bitcoin')

    def scraped_chart(currency_pair: str, row: Series) -> Dict:
        return {
            'measurement': 'scrapedChart',
            'tags': {
                'currencyPair': currency_pair,
            },
            'time': format_time(row.name),
            'fields': row.to_dict(),
        }

    def contemporary_usd_price(row) -> float:
        contemporary_btc_price = btc_price_hist['price_usd'].asof(row.name)
        return row['weightedAverage'] * contemporary_btc_price

    def historical_prices_of(
        pair: str,
        period: int = 900,
        start: Optional[float] = None,
        end: Optional[float] = None,
    ) -> Series:
        '''
        Returns a series of time-indexed prices.

        `pair` is of the form e.g. 'BTC_ETH',
        `period` is an integer number of seconds,
        either 300, 900, 1800, 7200, 14400, or 86400.
        '''
        now = time.time()
        start = start or now - YEAR_IN_SECS
        end = end or now

        ex_trades = polo.returnChartData(pair, period, start, end)
        ts_df = DataFrame(ex_trades, dtype=float)
        ts_df.index = [datetime.fromtimestamp(t) for t in ts_df['date']]
        ts_df = ts_df.drop(['date'], axis=1)
        ts_df['price_usd'] = ts_df.apply(contemporary_usd_price, axis=1)
        for _, row in ts_df.iterrows():
            chart = scraped_chart(pair, row)
            # for some reason, when there's no chart data to report,
            # the API will give us some reading with all 0s.
            if chart['fields']['volume'] == 0 and chart['fields']['weightedAverage'] == 0:
                # we will just ignore these
                pass
            else:
                yield chart

    # get the most recent chart data
    # already fetched from the db
    latest_result = client.query(
        ' '.join([
            'select * from scrapedChart',
            'order by time desc',
            'limit 1',
        ]),
    )

    # Get the last time we fetched some data,
    # looking at the most recent result in the db
    latest_fetch_time = parser.parse(
        # sorry this is hack city
        list(latest_result.get_points())[0]['time'])

    # convert from string to unix time
    latest_fetch_unix = time.mktime(latest_fetch_time.timetuple())

    # for each market,
    for market in polo.returnTicker():
        # fetch all the chart data
        # since that last fetch.
        # try:
        generator = historical_prices_of(
            market,
            start=latest_fetch_unix,
            end=time.time(),
        )
        client.write_points(generator)
        logger.debug(f'Scraped {market}')
        # except:
        #     logger.error(f'error scraping market: {market}')

    def marshall(hist_df, key='price_btc'):
        btc_to_usd = hist_df['price_usd'] / hist_df['price_btc']
        # volume in BTC
        hist_df['volume'] = hist_df['volume_usd'] / btc_to_usd
        hist_df = hist_df.drop([
            'market_cap_by_available_supply',
            'volume_usd'
        ], axis=1)
        hist_df = hist_df.rename(columns={key: 'weightedAverage'})
        return hist_df

    # Finally, write USD_BTC history to the client as well
    btc_rows = marshall(btc_price_hist, key='price_usd')
    client.write_points(scraped_chart('USD_BTC', row)
                        for _, row in btc_rows.iterrows())
    logger.debug('Scraped USD_BTC')


class MarketHistory:
    '''
    TODO Docstring
    '''

    def __init__(self) -> None:
        self.client = Postgres.get_client()

    def scrape_latest(self) -> None:
        return scrape_since_last_reading(self.client)

    # String -> { 'BTC_ETH': { weightedAverage, ...} ...}
    # TODO One issue here is that we are *only* getting the latest (15-minute) candlestic
    # So, if we are only trading once per day, certain values (like volume) will be misleading,
    # as they won't cover teh whole 24-hour period.
    # We could, in the future, address this by taking all the candlesticks since we last checked
    # and pass them through to the strategy together, sorted ny time.
    # Then, the strategy can then decide how to combine them.
    def latest(self, time: datetime) -> Dict[str, Dict[str, float]]:
        cursor = self.client.cursor()
        prior_date = time - timedelta(days=1)
        q = ' '.join([
            'select * from scrapedChart',
            f"where time <= '{time!s}' and time > '{prior_date!s}'",
            'group by currencyPair',
            'order by time desc',
        ])
        cursor.execute(q)
        results = cursor.fetchall()
        print(results)
        # result_set = self.client.query(q)
        # coin_generator_tuples = {
        #     r[0][1]['currencyPair']: list(r[1])[0]
        #     for r
        #     in result_set.items()
        # }
        return coin_generator_tuples

    def asset_history(
        self,
        time: datetime,
        base: str,
        quote: str,
        days_back: int=30,
        key: str ='price_usd',
    ) -> List[float]:
        currency_pair = f'{base}_{quote}'
        prior_date = time - timedelta(days=days_back)
        q = ' '.join([
            'select * from scrapedChart',
            f"where currencyPair='{currency_pair}'",
            f"and time <= '{time}' and time > '{time!s}' - {prior_date!s}d",
            'order by time desc',
        ])
        result_set = self.client.query(q)
        prices = [(p['time'], p[key]) for p in result_set.get_points()]
        df = Series([p[1] for p in prices])
        df.index = [p[0] for p in prices]
        return df
