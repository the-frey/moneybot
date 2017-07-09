# -*- coding: utf-8 -*-
import pytest
import staticconf
import yaml

import moneybot


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
