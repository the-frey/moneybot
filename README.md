# FundRunner

To use fund runner you create a custom trading strategy (or use one of the provided examples), which you can:
* Backtest over historical data
* Use on live trading.

See the `fundrunner/strategies` folder for examples.

## Install

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Finally, you will need Poloniex api keys. You can [generate those via the Poloniex web interface](https://www.youtube.com/watch?v=OScIbgXZoW0).

See the `config.json.example` file, add your Poloniex api keys and save it as `config.json`.

# Backtesting
For an example, see `example.py`.

You need to install [influxdb](https://www.influxdata.com/) (tested on v1.2.2), run it on `localhost:8086`, and download historical data for backtesting. Grab the [poloniex ticker database](https://bitbucket.org/peakrider/poloniex-ticker-history) (see that README for how to restore the InfluxDB, which we use for backtesting).

# Live trading

For an example, see `polo_purchase.py`

### Grafana

Finally, there is a grafana dashboard.

[Install Grafana](https://grafana.com/grafana/download) for your platform, and hook up Influx DB using the GUI.

Then, in Grafana's dashboard pane, import the .json file in the `grafana/` directory.
