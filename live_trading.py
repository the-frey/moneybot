from influxdb import InfluxDBClient
import json
from fundrunner.coinstore import HistoricalCoinStore, LiveCoinStore
from fundrunner.market import PoloniexMarket
from fundrunner.balances import Balances
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy
from fundrunner import Purchase
from datetime import datetime
import pandas as pd
from time import sleep

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

client = InfluxDBClient(config['db']['hostname'],
                        config['db']['port'],
                        config['db']['username'],
                        config['db']['password'],
                        config['db']['database'])

market = PoloniexMarket(config['poloniex']['pk'], config['poloniex']['sk'])

lcs = LiveCoinStore(client, market)
# see historical poloneix repo for minutes durations
# trading_frequency_minutes = 5

current_bals = market.get_balances()
strat = BuffedCoinStrategy(
  lcs,
  current_bals
)

strat.set_market(market)
strat.balances = Balances(pd.Timestamp(datetime.now()), current_bals)
while True:
	print(strat.step(pd.Timestamp(datetime.now())))
	sleep(300)
