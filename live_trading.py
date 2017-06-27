import json
from fundrunner.strategies.buffedcoinstrategy import BuffedCoinStrategy

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

strat = BuffedCoinStrategy(config)

strat.run_live()

