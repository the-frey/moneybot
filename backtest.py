from influxdb import InfluxDBClient
import json
from fundrunner.coinstore import HistoricalCoinStore
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

conditions = json.load(open('backtest-conditions.json', 'r'))

def test_over (strategy, market_condition, frequency_condition):
    start = conditions['market'][market_condition]['start']
    end   = conditions['market'][market_condition]['end']
    minutes = conditions['frequency'][frequency_condition]['trading_frequency_minutes']
    coinstore = HistoricalCoinStore(client, minutes)
    strat = strategy['fn'](
            coinstore,
            {'BTC': 1},)
    summary = evaluate(strat,
                       start, end,
                       duration_days=30,
                       verbose=True, window_distance_days=30,
                       trading_frequency_minutes=minutes)
    return summary

strategies = [
        {'name': 'buyholdstrategy', 'fn': BuyHoldStrategy, },
        {'name': 'buffedcoinstrategy', 'fn': BuffedCoinStrategy, },
        {'name': 'peakriderstrategy', 'fn': PeakRiderStrategy, },
]

print('starting')
rows = []
for market_condition in conditions['market']:
    print('market', market_condition)
    for frequency in conditions['frequency']:
        print('frequency', frequency)
        for strategy in strategies:
            summary = test_over(strategy, market_condition, frequency)
            summary['market_condition'] = market_condition
            summary['trading_frequency'] = frequency
            summary['strategy'] = strategy['name']
            rows.append(summary)
        # for freq in conditions['frequency']:
            # print(market, freq)

import pandas as pd
df = pd.DataFrame(rows)
df.to_csv('data-exploration/equal-weight-strategies-perfs.csv')
