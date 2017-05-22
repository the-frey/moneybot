import pandas as pd

class CoinStore(object):

    def __init__(self, influx_client):
        self.client = influx_client

    def available_coins (self, time):
        q ='''
        select * from ticker
        where time <= '{!s}' and time > '{!s}' - 1d
        group by coin
        order by time desc
        limit 1
        '''.format(time, time)
        result_set = self.client.query(q)
        coin_generator_tuples = { r[0][1]['coin']: list(r[1])[0]
                                 for r in result_set.items() }
        return coin_generator_tuples

    def coin_price_history (self, coin, time,
                            key='price_usd', days=30):
        q ='''
        select * from ticker
        where coin='{!s}'
        and time <= '{!s}' and time > '{!s}' - {!s}d
        order by time desc
        '''.format(coin, time, time, days)
        result_set = self.client.query(q)
        prices     = [(p['time'], p[key]) for p in result_set.get_points()]
        df = pd.Series([p[1] for p in prices])
        df.index = [p[0] for p in prices]
        return df
