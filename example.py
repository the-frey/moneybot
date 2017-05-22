from datetime import timedelta, date
from influxdb import InfluxDBClient
import json
from fundrunner.balances import Balances
from fundrunner.coinstore import CoinStore
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner.strategies.buyholdstrategy import BuyHoldStrategy

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

client = InfluxDBClient(config['db']['hostname'], 
                        config['db']['port'], 
                        config['db']['username'], 
                        config['db']['password'], 
                        config['db']['database'])

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

ex_start = date(2017, 2, 1)
ex_end   = date(2017, 4, 1)

strat = BuffedCoinStrategy(
# strat = BuyHoldStrategy(
    CoinStore(client),
    Balances(ex_start, {'BTC': 1}),
    ex_start, ex_end,
)

for date in daterange(ex_start, ex_end):
    bal, val = strat.step(date)
    print(val)
