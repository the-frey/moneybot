import json
from moneybot.Fund import Fund
from moneybot.market_adapters.LiveMarketAdapter import LiveMarketAdapter
from moneybot.strategies.BuffedCoinStrategy import BuffedCoinStrategy

with open('config.json') as cfg_file:
	config = json.load(cfg_file)

# strat = BuffedCoinStrategy(LiveMarketAdapter, config)
fund = Fund(BuffedCoinStrategy, LiveMarketAdapter, config)
fund.run_live()

