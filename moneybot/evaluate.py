# -*- coding: utf-8 -*-
from multiprocessing import Pool
from typing import List
from typing import Tuple

from numpy import mean
from pandas import date_range
from pandas import Series
from pandas import Timestamp

from moneybot.Fund import Fund


def roi(values: List[float]) -> float:
    return (values[-1] - values[0]) / values[0]


def max_drawdown(values: List[float]) -> float:
    maximum = max(values)
    idxmax = values.index(maximum)
    subsequent = values[idxmax:]
    return (maximum - min(subsequent)) / maximum


def sterling_ratio(
    many_values: List[List[float]],
    days_per_simulation: int,
    risk_free_rate: float = 0.0091,
) -> float:
    rate_per_day = risk_free_rate / 90
    adjusted_rate = rate_per_day * days_per_simulation
    rs = [roi(v) for v in many_values]
    max_drawdowns = list(map(max_drawdown, many_values))
    return (mean(rs) - adjusted_rate) / mean(max_drawdowns)


# # return over max drawdown
# def RoMaD (values):
#     my_roi = roi(values)
#     max_dd = max_drawdown(values)
#     if max_dd != 0:
#         return  my_roi / max_dd
#     return my_roi


def summary(
    many_values: List[List[float]],
    days_per_simulation: int,
) -> Series:
    rois = Series([roi(values) for values in many_values])
    rois_desc = rois.describe()
    rois_desc['sterling_ratio'] = sterling_ratio(many_values, days_per_simulation)
    return rois_desc


# This needs to be a top-level method
# So that it can be pickled by multiprocessing.Pool
def backtest(fund_dates: Tuple[Fund, str, str]) -> List[float]:
    fund, start, end = fund_dates
    print('Testing from {!s} to {!s}'.format(start, end))
    return list(fund.begin_backtest(start, end))


def evaluate(
    fund: Fund,
    start_date: str,
    end_date: str,
    duration_days: int = 90,
    window_distance_days: int = 30,
    verbose: bool = True,
    num_threads: int = 4,
) -> Series:
    start = Timestamp(start_date)
    end = Timestamp(end_date)
    start_times = date_range(start, end, freq='{!s}d'.format(window_distance_days))

    # We make tuples of (Fund, Date, Date)
    # This gets passed to `backtest()` using Pool().map()
    time_tuples = []
    for i, start_time in enumerate(start_times[:-1]):
        time_tuple = (fund, start_time, start_times[i + 1])
        time_tuples.append(time_tuple)

    with Pool(num_threads) as p:
        results = p.map(backtest, time_tuples)
        return summary(results, duration_days)
