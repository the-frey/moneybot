import pandas as pd

class CoinStore(object):

    def __init__(self, influx_client, minutes_candlestick_duration):

        self.minutes = minutes_candlestick_duration
        self.client = influx_client

    def available_markets (self, time):
        q ='''
        select * from candlestick
        where minutes = '{!s}'
        and time <= '{!s}' and time > '{!s}' - 1d
        and currencyPair != 'USD_BTC'
        group by currencyPair
        order by time desc
        limit 1
        '''.format(self.minutes, time, time)
        result_set = self.client.query(q)
        coin_generator_tuples = { r[0][1]['currencyPair']: list(r[1])[0]
                                 for r in result_set.items() }
        return coin_generator_tuples

    def btc_price (self, time,
                   key='average'):
        q ='''
        select * from candlestick
        where minutes = '{!s}'
        and time <= '{!s}' and time > '{!s}' - 30d
        and currencyPair = 'USD_BTC'
        order by time desc
        limit 1
        '''.format(self.minutes, time, time)
        result_set = self.client.query(q)
        return list(result_set.get_points())[-1][key]

    def market_history (self, currency_pair, time,
                            days_back=30, key='average'):
        q ='''
        select * from candlestick
        where currencyPair='{!s}'
        and minutes='{!s}'
        and time <= '{!s}' and time > '{!s}' - {!s}d
        order by time desc
        '''.format(currency_pair, self.minutes, time, time, days_back)
        result_set = self.client.query(q)
        prices     = [(p['time'], p[key]) for p in result_set.get_points()]
        df = pd.Series([p[1] for p in prices])
        df.index = [p[0] for p in prices]
        return df
