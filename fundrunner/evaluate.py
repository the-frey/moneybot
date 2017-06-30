import pandas as pd
from datetime import timedelta
from multiprocessing import Pool
import numpy as np


def roi (values):
    return (values[-1] - values[0]) / values[0]


def max_drawdown (values):
    maximum = max(values)
    idxmax = values.index(maximum)
    subsequent = values[idxmax:]
    return (maximum - min(subsequent)) / maximum


def sterling_ratio (many_values, days_per_simulation,
                    risk_free_rate = 0.0091):
    rate_per_day  = risk_free_rate/90
    adjusted_rate = rate_per_day * days_per_simulation
    rs            = [roi(v) for v in many_values]
    max_drawdowns = list(map(max_drawdown, many_values))
    return (np.mean(rs) - adjusted_rate) / np.mean(max_drawdowns)


# # return over max drawdown
# def RoMaD (values):
#     my_roi = roi(values)
#     max_dd = max_drawdown(values)
#     if max_dd != 0:
#         return  my_roi / max_dd
#     return my_roi


def summary (many_values, days_per_simulation):
    rois = pd.Series([roi(values) for values in many_values])
    rois_desc = rois.describe()
    rois_desc['sterling_ratio'] = sterling_ratio(many_values, days_per_simulation)
    return rois_desc


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
        time_tuple = (strategy, start_time, start_times[i+1])
        time_tuples.append(time_tuple)

    with Pool(num_threads) as p:
        results = p.map(backtest, time_tuples)
        return summary(results, duration_days)
