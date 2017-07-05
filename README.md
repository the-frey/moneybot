# MoneyBot

To use fund runner you create a custom trading strategy (or use one of the provided examples), which you can:
* Backtest over historical data
* Use on live trading.

See the `fundrunner/strategies` folder for examples.

## Install

First, install Python dependencies.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Next, install [InfluxDB](https://infuxdata.com) for your platform.
Restore [the most recent seed database](https://github.com/elsehow/moneybot/releases/tag/database) to your Influx instance for backtesting.
(This database will be updated automatically during live-trading, so you should only need to do this upon initial setup).
See [Restoring influxDB](https://docs.influxdata.com/influxdb/v1.2/administration/backup_and_restore/#restore) for more information.

Finally, you will need Poloniex api keys. You can [generate those via the Poloniex web interface](https://www.youtube.com/watch?v=OScIbgXZoW0).
See the `config.json.example` file, add your Poloniex api keys and save it as `config.json`.

# Backtesting
For an example, see `example.py`.

You need to install [influxdb](https://www.influxdata.com/) (tested on v1.2.2), run it on `localhost:8086`, and download historical data for backtesting. 

# Live trading

For an example, see `polo_purchase.py`

# license

BSD
