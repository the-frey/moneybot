import numpy as np
import pandas as pd

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
