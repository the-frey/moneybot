# -*- coding: utf-8 -*-
import pytest
import staticconf
import yaml

import moneybot
from moneybot.clients import InfluxDB


TEST_CONFIG = """
influxdb:
  host: localhost
  port: 8086
  username: root
  password: root
  database: historical-poloniex

trading:
  fiat: BTC
  interval: 86400
"""


@pytest.fixture(scope='session', autouse=True)
def config():
    staticconf.DictConfiguration(
        yaml.load(TEST_CONFIG),
        namespace=moneybot.CONFIG_NS,
    )


@pytest.fixture(scope='session', autouse=True)
def db(config):
    client = InfluxDB.get_client()
    # db_name = moneybot.config.read_string('influxdb.database')
    # client.create_database(db_name)
    return client
