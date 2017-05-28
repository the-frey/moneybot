import pandas as pd
from datetime import timedelta
from fundrunner.metrics import summary

def evaluate (strategy, start_date, end_date,
                   duration_days = 90, window_distance_days = 30,
                   trading_frequency_minutes = 1440, verbose = True):

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date) - timedelta(days=duration_days)
    start_times = pd.date_range(start, end, freq='{!s}d'.format(window_distance_days))
    all_vals = []

    for start_time in start_times:
        if verbose:
            print('{!s} for {!s} days trading every {!s} minutes'\
                  .format(start_time, duration_days, trading_frequency_minutes))
        dates = pd.date_range(start_time,
                              start_time + timedelta(days=duration_days),
                              freq='{!s}T'.format(trading_frequency_minutes))
        vals = strategy.begin_backtest(dates)
        all_vals.append(list(vals))

    return summary(all_vals, duration_days)
