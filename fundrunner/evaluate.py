import pandas as pd
from datetime import timedelta
from fundrunner.metrics import summary
from multiprocessing import Pool

# This needs to be a top-level method
# So that it can be pickled by multiprocessing.Pool
def backtest (strategy_dates):
    strategy, dates = strategy_dates
    print('Testing from {!s} to {!s} at intervals of {!s}'.format(
        dates[0], dates[-1], dates[1]-dates[0]))
    return list(strategy.begin_backtest(dates))


def evaluate (strategy, start_date, end_date,
              duration_days = 90, window_distance_days = 30,
              verbose = True,
              trading_duration_seconds=900,
              num_threads=4):


    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date) - timedelta(days=duration_days)
    start_times = pd.date_range(start, end, freq='{!s}d'.format(window_distance_days))

    # We make tuples of (strategy, List<Date>)
    # This gets passed to `backtest()` using Pool().map()
    strat_dates_tuples = []
    for start_time in start_times:
        dates = pd.date_range(start_time,
                              start_time + timedelta(days=duration_days),
                              freq='{!s}s'.format(trading_duration_seconds))
        strat_dates_tuples.append((strategy, dates))

    with Pool(num_threads) as p:
        return summary(
            p.map(backtest, strat_dates_tuples),
            duration_days
        )
