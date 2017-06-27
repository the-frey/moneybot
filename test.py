from influxdb import InfluxDBClient
import json
from fundrunner.coinstore import HistoricalCoinStore
from fundrunner.strategies.buyholdstrategy import BuyHoldStrategy
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner.strategies.peakriderstrategy import PeakRiderStrategy
import pandas as pd

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

client = InfluxDBClient(config['db']['hostname'],
                        config['db']['port'],
                        config['db']['username'],
                        config['db']['password'],
                        config['db']['database'])

coinstore = HistoricalCoinStore(client)

expected_results = [
    {
        'strategy': BuffedCoinStrategy,
        'values': [1314.97, 1247.06, 1315.55, 1352.14, 1556.81, 1698.24, 1936.8, 1926.03, 1931.84, 2108.54, 1980.2, 2207.76, 2358.78, 2456.38, 2519.19, 2430.25, 2434.34, 2804.8, 2981.39, 3357.73, 3756.43, 3723.49, 4186.68, 4461.88, 4100.53, 4824.85, 3478.72, 3344.19, 3525.7, 3648.75, 3881.41, 3971.18]
    },
    {
        'strategy': BuyHoldStrategy,
        'values': [1314.97, 1247.06, 1315.55, 1352.14, 1556.9, 1702.35, 1948.89, 1999.39, 1931.33, 2140.16, 1966.29, 2224.67, 2378.23, 2423.56, 2449.02, 2391.89, 2397.69, 2790.64, 2922.69, 3291.85, 3813.61, 3889.25, 4180.43, 4424.93, 3891.9, 4702.14, 3333.39, 3214.08, 3385.25, 3530.77, 3780.49, 3792.21]
    },
]


import unittest

class TestFundRunner (unittest.TestCase):
    def test_strategies (self):
        for expected in expected_results:
            '''
            Strategies should produce their expected values
            '''
            # Try BuyHoldStrategy or BuffedCoinStrategy too
            strat = expected['strategy'](
                coinstore,
                {'BTC': 1},)
            start = pd.Timestamp('2017-05-01')
            end = pd.Timestamp('2017-06-01')
            start_times = pd.date_range(start, end, freq='1d')
            res = list(strat.begin_backtest(start_times))
            self.assertListEqual(res, expected['values'])

    def test_all_results_diff (self):
        '''
        No two results should be equal.
        '''
        for i, expected in enumerate(expected_results[:-1]):
            self.assertNotEqual(
                expected,
                expected_results[i+1])

if __name__ == '__main__':
    print('Starting tests.')
    unittest.main()
