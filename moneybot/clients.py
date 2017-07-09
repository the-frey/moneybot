# -*- coding: utf-8 -*-
from influxdb import InfluxDBClient
from poloniex import Poloniex as _Poloniex

from moneybot import config


class InfluxDB:

    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = InfluxDBClient(
                config.read_string('influxdb.host'),
                config.read_int('influxdb.port'),
                config.read_string('influxdb.username'),
                config.read_string('influxdb.password'),
                config.read_string('influxdb.database'),
            )
        return cls._client


class Poloniex:

    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = _Poloniex(
                config.read_string('poloniex.key', default=None),
                config.read_string('poloniex.secret', default=None),
            )
        return cls._client
