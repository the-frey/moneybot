import json
from fundrunner.strategies.buyholdstrategy import BuyHoldStrategy
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner.strategies.peakriderstrategy import PeakRiderStrategy
import pandas as pd

with open('config.json.example') as cfg_file:
	config = json.load(cfg_file)

# The start and end of our test period
start = '2017-05-01'
end = '2017-06-01'
# Each strategy, and the USD values it should produce after 
# each step through the series of trade-times.
expected_results = [
    {
        'strategy': BuffedCoinStrategy,
            'values': [1318.21, 1250.13, 1318.79, 1355.47, 1560.75, 1694.85, 1918.27, 1866.54, 1888.66, 2039.06, 1967.42, 2184.11, 2326.3, 2461.91, 2589.18, 2544.36, 2420.49, 2778.22, 2958.32, 3313.64, 3686.43, 3704.98, 4091.39, 4400.23, 4135.33, 4887.53, 3549.03, 3364.61, 3581.18, 3743.0, 4268.86, 4319.96]
    },
    {
        'strategy': BuyHoldStrategy,
        'values': [1318.21, 1250.13, 1318.79, 1355.47, 1560.75, 1706.55, 1953.71, 2004.34, 1936.11, 2145.46, 1971.15, 2230.17, 2384.13, 2429.57, 2455.09, 2397.81, 2403.63, 2797.57, 2929.94, 3300.03, 3823.09, 3898.91, 4190.82, 4435.93, 3901.56, 4713.82, 3341.65, 3222.06, 3393.65, 3539.53, 3789.87, 3801.63]
    },
    # {
    #     'strategy': PeakRiderStrategy,
    #     'values': [1318.21, 1250.13, 1318.79, 1355.47, 1560.75, 1706.55, 1920.65, 1889.18, 1906.54, 2071.08, 1947.65, 2156.81, 2296.88, 2381.47, 2439.71, 2317.35, 2315.89, 2593.93, 2707.41, 2988.51, 3286.22, 3273.72, 3667.68, 3929.34, 3696.06, 4301.23, 3168.55, 3026.37, 3156.56, 3240.11, 3298.35, 3392.31]
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
            self.assertListEqual(res, expected['values'])

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
