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
strat = PeakRiderStrategy(
    coinstore,
    {'BTC': 1},)

summary = evaluate(strat,
                   '2017-06-01', '2017-06-19',
                   duration_days=18,
                   window_distance_days=30)

print(summary)
