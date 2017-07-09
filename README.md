# MoneyBot

MoneyBot allows you to backtest trading strategies, and deploy these strategies to live-trade, without changing code.

For now, MoneyBot only supports Poloniex. However, a generic `MarketAdapter` pattern could allow trading over many exchanges. PRs welcome!

# install

First, install Python dependencies.

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

Install [InfluxDB](https://influxdata.com) for your platform. On macOS, this is as easy as `$ brew install influxdb` (assuming you have Homebrew installed). We're working on making it possible to run this in a Docker container as well, but there is [a blocker](https://github.com/influxdata/influxdb/issues/8551) currently.

To do backtesting, you'll need to populate InfluxDB with historical data. Check [the releases page](https://github.com/elsehow/moneybot/releases/tag/database) for the latest version of the seed database. This database will be updated automatically during live-trading, so you should only need to do this upon initial setup. The restore process is a [little complicated](https://docs.influxdata.com/influxdb/v1.2/administration/backup_and_restore/#restore) so we have a script that does the heavy lifting. It is configured with environment variables, so adjust the example below to suit your setup:

```
$ DB_RELEASE=7-5-2017 DB_NAME=historical-poloniex INFLUX_DIR=/usr/local/var/influxdb ./local-services/influxdb/restore.sh
```

# test

First, install [`tox`](https://tox.readthedocs.io/en/latest/):

```
$ pip3 install tox
```

The tests assume InfluxDB is reachable at localhost:8086 (see [tests/conftest.py](https://github.com/elsehow/moneybot/blob/master/tests/conftest.py)). If your setup is different, modify the `config` fixture accordingly (or if it's different for enough people we can use an env var or something).

To run the tests:

```
$ tox
```

This runs `mypy` over the `moneybot/` and `tests/` directories, then invokes [`pytest`](https://docs.pytest.org/en/latest/contents.html) on the `tests/` directory.

To recreate the testing environment (necessary when dependency versions change), add `-r` or `--recreate`. To run `pytest` with more detailed output, add `-e verbose`.

# use

Make sure InfluxDB is running.

There are a few `Strategy` implementations in `moneybot.examples.strategies`.

>The strategies included herein are viable for live-trading use, but crypto trading is serious business. It's entirely possible to lose a lot of money, very quickly. The authors of this library provide these for the sake of illustration and assume no responsibility for their performance if deployed.

## backtesting

```
$ python3 examples/backtest.py -c config.yml -s buffed-coin
```

## live trading

**NOTE**: See disclaimer!

To live-trade, you will need Poloniex API keys. You can generate those via the [Poloniex web interface](https://www.youtube.com/watch?v=OScIbgXZoW0). You'll only need to allow "trading" permissions on the keys. See the `config-example.yaml` file, add your Poloniex credentials and save it as `config.yml`.

```
$ python3 examples/live_trading.py -c config.yml -s buffed-coin
```

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
