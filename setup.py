#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


setup(
    name='moneybot',
    version='0.0.1',

    packages=find_packages(),

    install_requires=[
        'funcy',
        'influxdb',
        'numpy',
        'pandas',
        # 'poloniex',
        'requests',
    ],

    author='Nick Merrill',
    author_email='yes@cosmopol.is',
    description='backtest (and deploy) cryptocurrency trading strategies',
    url='https://github.com/elsehow/moneybot',
)
