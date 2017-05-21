class CoinStore(object):
    def __init__(self, influx_client):
        self.client = influx_client
    def see_available_coins (self, time):
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
