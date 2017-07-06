import json
from moneybot.Fund import Fund
from moneybot.market_adapters.BacktestMarketAdapter import BacktestMarketAdapter
from moneybot.strategies.BuyHoldStrategy import BuyHoldStrategy
from moneybot.strategies.BuffedCoinStrategy import BuffedCoinStrategy
from moneybot.strategies.PeakRiderStrategy import PeakRiderStrategy
from moneybot.evaluate import evaluate

with open('config.json.example') as cfg_file:
	config = json.load(cfg_file)

# Try BuyHoldStrategy or BuffedCoinStrategy too
strat = Fund(BuffedCoinStrategy, BacktestMarketAdapter, config)

summary = evaluate(strat,
                   '2017-01-01', '2017-06-29',
                   duration_days=30,
                   window_distance_days=14)

print(summary)
