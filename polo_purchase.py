from influxdb import InfluxDBClient
import json
from fundrunner.coinstore import LiveCoinStore
from fundrunner.market import PoloniexMarket
from fundrunner.balances import Balances
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner import Purchase
from datetime import datetime
import pandas as pd

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

client = InfluxDBClient(config['db']['hostname'],
                        config['db']['port'],
                        config['db']['username'],
                        config['db']['password'],
                        config['db']['database'])

market = PoloniexMarket(config['poloniex']['pk'], config['poloniex']['sk'])
# print(market.get_balances())
lcs = LiveCoinStore(market)
print(lcs.btc_price())

current_bals = market.get_balances()
strat = BuffedCoinStrategy(
  lcs,
  current_bals
)

strat.set_market(market)
print(current_bals)

strat.balances = Balances(pd.Timestamp(datetime.now()), current_bals)
print(strat.step(pd.Timestamp(datetime.now())))
