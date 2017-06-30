import json
from fundrunner.market_adapters.BacktestMarketAdapter import BacktestMarketAdapter
from fundrunner.strategies.buyholdstrategy import BuyHoldStrategy
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner.strategies.peakriderstrategy import PeakRiderStrategy

from fundrunner.evaluate import evaluate

with open('config.json.example') as cfg_file:
	config = json.load(cfg_file)

# Try BuyHoldStrategy or BuffedCoinStrategy too
strat = BuffedCoinStrategy(BacktestMarketAdapter, config)

summary = evaluate(strat,
                   '2017-01-01', '2017-06-29',
                   duration_days=30,
                   window_distance_days=14)

print(summary)
