import json
from fundrunner.strategies.buyholdstrategy import BuyHoldStrategy
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner.strategies.peakriderstrategy import PeakRiderStrategy
import pandas as pd

with open('config.backtest.json') as cfg_file:
	config = json.load(cfg_file)

# The start and end of our test period
start = '2017-05-01'
end = '2017-06-01'
# Each strategy, and the USD values it should produce after 
# each step through the series of trade-times.
expected_results = [
    {
        'strategy': BuffedCoinStrategy,
        'values': [1314.97, 1247.06, 1315.55, 1352.14, 1556.81, 1698.24, 1936.8, 1926.03, 1931.84, 2108.54, 1980.2, 2207.76, 2358.78, 2456.38, 2519.19, 2430.25, 2434.34, 2804.8, 2981.39, 3357.73, 3756.43, 3723.49, 4186.68, 4461.88, 4100.53, 4824.85, 3478.72, 3344.19, 3525.7, 3648.75, 3881.41, 3971.18]
    },
    {
        'strategy': BuyHoldStrategy,
        'values': [1314.97, 1247.06, 1315.55, 1352.14, 1556.9, 1702.35, 1948.89, 1999.39, 1931.33, 2140.16, 1966.29, 2224.67, 2378.23, 2423.56, 2449.02, 2391.89, 2397.69, 2790.64, 2922.69, 3291.85, 3813.61, 3889.25, 4180.43, 4424.93, 3891.9, 4702.14, 3333.39, 3214.08, 3385.25, 3530.77, 3780.49, 3792.21]
    },
    # {
    #     'strategy': PeakRiderStrategy,
    #     'values': [1314.97, 1247.06, 1315.55, 1352.14, 1556.9, 1702.28, 1932.53, 1942.7, 1909.26, 2096.03, 1953.89, 2175.22, 2319.52, 2378.08, 2421.37, 2324.02, 2330.57, 2680.09, 2805.82, 3134.95, 3476.77, 3435.99, 3843.79, 4085.97, 3723.58, 4392.44, 3157.82, 3046.51, 3210.41, 3318.21, 3541.0, 3569.73],
    # },
]


import unittest

class TestFundRunner (unittest.TestCase):
    def test_strategies (self):
        for expected in expected_results:
            '''
            Strategies should produce their expected values
            '''
            # Try BuyHoldStrategy or BuffedCoinStrategy too
            strat = expected['strategy'](config)
            res = list(strat.begin_backtest(start, end))
            self.assertListEqual(res, expected['values'],
                                 # log message
                                 expected['strategy']
                                 )

    def test_all_results_diff (self):
        '''
        No two results should be equal.
        '''
        for i, expected in enumerate(expected_results[:-1]):
            self.assertNotEqual(
                expected,
                expected_results[i+1],
                "no two expected results are the same"
                )

if __name__ == '__main__':
    print('Starting tests.')
    unittest.main()
