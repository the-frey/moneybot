# -*- coding: utf-8 -*-
import json

import pytest
from influxdb import InfluxDBClient


TEST_CONFIG = """
{
  "db": {
    "hostname": "192.168.99.100",
    "port": 8086,
    "username": "root",
    "password": "root",
    "database": "historical-poloniex"
  },

  "backtesting": {
    "initial_balances": {
      "BTC": 1
    }
  },

  "livetrading": {
    "poloniex": {
      "pk": "YOUR_API_KEY",
      "sk": "YOUR_API_SECRET"
    }
  },

  "trade_interval": 86400,
  "fiat": "BTC"
}
"""


@pytest.fixture(scope='session')
def config():
    return json.loads(TEST_CONFIG)


@pytest.fixture(scope='session', autouse=True)
def db(config):
    client = InfluxDBClient(
        config['db']['hostname'],
        config['db']['port'],
        config['db']['username'],
        config['db']['password'],
        config['db']['database'],
    )
    client.create_database(config['db']['database'])
    return client
