# Roadmap

Feel free to reorganize or make suggestions based on what you think is priority and realistic for where the codebase is now.

## refactor

* Create a LiveMarketAdapter and a BacktestMarketAdapter
  * Possibly live in different files

* Bring in the scraper
    * Should auto- backfill when trading live.

* Optional but nice
    * Asset blacklist in config - backtest that!
    * Replace with proper logging everywhere
    * Strategy shouldn't have access to MarketAdapter.execute()

## backtest

* Blacklist for coins

## live-trading

* ~~Fix cancel and rebuy: open orders are a pain in the ass~~
* Withdraw: as a user I would like withdraw an ammount from my indux fund and have it be applied easily

