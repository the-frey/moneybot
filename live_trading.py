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

strat = BuffedCoinStrategy(config)
#   lcs,
#   current_bals
# )
# interval = config['period'] or 300
while True:
	print(strat.step(pd.Timestamp(datetime.now())))
	sleep(config['trade_interval']) #interval)
