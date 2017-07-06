# MoneyBot

MoneyBot allows you to backtest trading strategies, and deploy these strategies to live-trade, without changing code.

For now, MoneyBot only supports Poloniex. However, a generic `MarketAdapter` pattern could allow trading over many exchanges. PRs welcome!

# install

First, install Python dependencies.

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Next, install [InfluxDB](https://infuxdata.com) for your platform.
Restore [the most recent seed database](https://github.com/elsehow/moneybot/releases/tag/database) to your Influx instance for backtesting.
(This database will be updated automatically during live-trading, so you should only need to do this upon initial setup).
See [Restoring influxDB](https://docs.influxdata.com/influxdb/v1.2/administration/backup_and_restore/#restore) for more information.

# use

First, make sure Influx is running.

For an example of backtesting,

    python3 backtest.py

You can view the strategies in `strategies/BuffedCoinStrategy.py` for an example, if you're interested in writing your own strategy!

## live trading

(**NOTE**: See disclaimer!)
If you want to live-trade, 
you will need Poloniex API keys. You can [generate those via the Poloniex web interface](https://www.youtube.com/watch?v=OScIbgXZoW0).
You'll only need to allow "trading" permissions on the keys.
See the `config.json.example` file, add your Poloniex api keys and save it as `config.json`.

For an example, see `live_trading.py`

# disclaimer

Use MoneyBot AT YOUR OWN RISK. Specifically, 

- Backtests are no guarantee of future/live performance. 
- MoneyBot relies on 3rd-party APIs, like Poloniex, which may fail at anytime.
- MoneyBot is experimental software, and also may fail at any time.
- Running a bot, and trading in general, requires careful study of the risks, and parameters. Wrong settings can cause a major loss.
- Never leave MoneyBot un-monitored for long periods of time. Be prepared to stop it if too much loss occurs.

*You alone* are responsible for anything that happens when you're live-trading!

# license

BSD
