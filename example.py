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

# see historical poloneix repo for minutes durations
trading_frequency_minutes = 1440

coinstore = CoinStore(client, trading_frequency_minutes)

# strat = BuyHoldStrategy(
# strat = BuffedCoinStrategy(
strat = PeakRiderStrategy(
    coinstore,
    {'BTC': 1},)

summary = evaluate(strat,
                   '2017-01-01', '2017-05-26',
                   duration_days=30,
                   verbose=True, window_distance_days=30,
                   trading_frequency_minutes=trading_frequency_minutes)

print(summary)
