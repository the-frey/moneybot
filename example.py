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

coinstore = HistoricalCoinStore(client)

# Try BuyHoldStrategy or BuffedCoinStrategy too
strat = BuffedCoinStrategy(
    coinstore,
    {'BTC': 1},)

day_in_secs = 86400
summary = evaluate(strat,
                   '2017-03-01', '2017-06-26',
                   duration_days=30,
                   window_distance_days=14,
                   trading_duration_seconds=day_in_secs)
                   # trading_duration_seconds=day_in_secs//8)

print(summary)
