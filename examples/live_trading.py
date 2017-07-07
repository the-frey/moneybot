# -*- coding: utf-8 -*-
import json

from moneybot.fund import Fund
from moneybot.markets.adapters.live import LiveMarketAdapter
from moneybot.strategies.buffed_coin import BuffedCoinStrategy


with open('config.json') as cfg_file:
    config = json.load(cfg_file)

# strat = BuffedCoinStrategy(LiveMarketAdapter, config)
fund = Fund(BuffedCoinStrategy, LiveMarketAdapter, config)
fund.run_live()
