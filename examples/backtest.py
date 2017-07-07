# -*- coding: utf-8 -*-
import json
import logging
from argparse import ArgumentParser

from moneybot.evaluate import evaluate
from moneybot.fund import Fund
from moneybot.markets.adapters.backtest import BacktestMarketAdapter
from moneybot.strategies.buffed_coin import BuffedCoinStrategy


def main(args):
    with open(args.config) as cfg_file:
        config = json.load(cfg_file)

    # Try BuyHoldStrategy or BuffedCoinStrategy too
    strat = Fund(BuffedCoinStrategy, BacktestMarketAdapter, config)

    summary = evaluate(
        strat,
        '2017-01-01',
        '2017-06-29',
        duration_days=30,
        window_distance_days=14,
    )

    print(summary)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        default='config.json.example',
        type=str,
        help='path to config file',
    )
    parser.add_argument(
        '-l', '--log-level',
        default='INFO',
        type=str,
        choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Python logging level',
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    main(args)
