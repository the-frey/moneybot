import pandas as pd
from datetime import timedelta
from fundrunner.metrics import summary
from multiprocessing import Pool

# This needs to be a top-level method
# So that it can be pickled by multiprocessing.Pool
def backtest (strategy_dates):
    strategy, start, end = strategy_dates
    print('Testing from {!s} to {!s}'.format(start, end))
    return list(strategy.begin_backtest(start, end))


def evaluate (strategy, start_date, end_date,
              duration_days = 90, window_distance_days = 30,
              verbose = True, num_threads=4):

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    start_times = pd.date_range(start, end, freq='{!s}d'.format(window_distance_days))

    # We make tuples of (Strategy, Date, Date)
    # This gets passed to `backtest()` using Pool().map()
    time_tuples = []
    for i, start_time in enumerate(start_times[:-1]):
        time_tuples.append(
            (strategy, start_time, start_times[i+1])
            )

    with Pool(num_threads) as p:
        return summary(

            p.map(backtest, time_tuples),
            duration_days
        )
