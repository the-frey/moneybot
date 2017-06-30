import json
from moneybot.market_adapters.LiveMarketAdapter import LiveMarketAdapter
from moneybot.strategies.buffedcoinstrategy import BuffedCoinStrategy

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

strat = BuffedCoinStrategy(LiveMarketAdapter, config)

strat.run_live()

