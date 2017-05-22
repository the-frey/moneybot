from influxdb import InfluxDBClient
import json
from fundrunner.coinstore import CoinStore
from fundrunner.strategies.buyholdstrategy import BuyHoldStrategy
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner.strategies.peakriderstrategy import PeakRiderStrategy

from fundrunner.evaluate import evaluate

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

client = InfluxDBClient(config['db']['hostname'],
                        config['db']['port'],
                        config['db']['username'],
                        config['db']['password'],
                        config['db']['database'])

coinstore = CoinStore(client)
conditions = json.load(open('backtest-conditions.json', 'r'))


def test_over (strat, market_condition, frequency_condition):
    start = conditions['market'][market_condition]['start']
    end   = conditions['market'][market_condition]['end']
    hrs   = conditions['frequency'][frequency_condition]['trading_frequency_hours']
    return evaluate(strat,
                    start, end, duration_days=30,
                    verbose=True, window_distance_days=30,
                    trading_frequency_hours=hrs)

strategies = [
        {'name': 'buyholdstrategy', 'fn': BuyHoldStrategy, },
        {'name': 'buffedcoinstrategy', 'fn': BuffedCoinStrategy, },
        {'name': 'peakriderstrategy', 'fn': PeakRiderStrategy, },
]

print('starting')
# summary = test_over(strat, 'bull', 'medieval')
# print(summary)
rows = []
for market_condition in conditions['market']:
    print('market', market_condition)
    for frequency in conditions['frequency']:
        print('frequency', frequency)
        for strategy in strategies:
            strat = strategy['fn'](
                coinstore,
                {'BTC': 1},)
            summary = test_over(strat, market_condition, frequency)
            summary['market_condition'] = market_condition
            summary['trading_frequency'] = frequency
            summary['strategy'] = strategy['name']
            rows.append(summary)
        # for freq in conditions['frequency']:
            # print(market, freq)

import pandas as pd
df = pd.DataFrame(rows)
df.to_csv('data-exploration/equal-weight-strategies-perfs.csv')
