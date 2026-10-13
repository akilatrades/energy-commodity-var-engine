"""3-2-1 crack spread history and a pre-specified mean-reversion test.

Prices are front-month futures proxies: WTI crude (CL) in USD/bbl, RBOB gasoline
(RB) and NY Harbor ULSD / heating oil (HO) in USD/gal. Cracks are USD/bbl.
"""

import numpy as np
import pandas as pd
from scipy import stats

GALLONS_PER_BARREL = 42

# Fixed before the signal was evaluated; see README.
WINDOW = 60
ENTRY_Z = 1.5
# WTI settled at -$37.63 on April 20, 2020; these day-to-day changes are
# driven by that expiry, not by refining economics.
NEGATIVE_WTI_DATES = pd.to_datetime(["2020-04-20", "2020-04-21", "2020-04-22"])


def gasoline_crack(cl, rb):
    return rb * GALLONS_PER_BARREL - cl


def distillate_crack(cl, ho):
    return ho * GALLONS_PER_BARREL - cl


def crack_321(cl, rb, ho):
    """Three barrels of crude into two of gasoline and one of distillate, per bbl."""
    return (2 * rb * GALLONS_PER_BARREL + ho * GALLONS_PER_BARREL - 3 * cl) / 3


def load_prices(path):
    prices = pd.read_csv(path, parse_dates=["date"]).set_index("date")
    prices = prices.rename(columns={"CL=F": "cl", "RB=F": "rb", "HO=F": "ho"})
    if prices.index.duplicated().any() or not prices.index.is_monotonic_increasing:
        raise ValueError("Dates must be unique and in order")
    if prices[["cl", "rb", "ho"]].isna().any().any():
        raise ValueError("Missing prices; do not fill")
    return prices[["cl", "rb", "ho"]]


def crack_history(prices):
    out = pd.DataFrame(index=prices.index)
    out["gasoline_crack"] = gasoline_crack(prices.cl, prices.rb)
    out["distillate_crack"] = distillate_crack(prices.cl, prices.ho)
    out["crack_321"] = crack_321(prices.cl, prices.rb, prices.ho)
    return out


def contract_roll_days(index):
    """First trading day of each month.

    RBOB and heating oil futures expire on the last business day of the month,
    so a continuous front-month series switches contracts on the next trading
    day. The crack change on that day mixes two delivery months.
    """
    dates = index.to_series()
    first = dates.groupby(index.to_period("M")).transform("min")
    return pd.Series(first.values == index.values, index=index)


def excluded_days(index):
    return contract_roll_days(index) | pd.Series(
        index.isin(NEGATIVE_WTI_DATES), index=index
    )


def zscore(crack, window=WINDOW):
    """Uses only prices up to and including each date."""
    mean = crack.rolling(window).mean()
    std = crack.rolling(window).std()
    return (crack - mean) / std


def mean_reversion_position(z, entry=ENTRY_Z):
    """Short the crack when it is stretched high, long when stretched low."""
    position = pd.Series(np.where(z > entry, -1, np.where(z < -entry, 1, 0)), z.index)
    return position.where(z.notna())


def next_day_pnl(crack, position, exclude=None):
    """P&L per barrel from holding the position set at close t until close t+1.

    Days whose next-day change is excluded (roll days, negative WTI) are dropped.
    """
    change = crack.shift(-1) - crack
    frame = pd.DataFrame({"position": position, "next_change": change})
    if exclude is not None:
        frame = frame[~exclude.shift(-1, fill_value=True)]
    frame = frame.dropna()
    frame["pnl"] = frame.position * frame.next_change
    return frame


def summarize(frame, label):
    active = frame[frame.position != 0]
    test = stats.ttest_1samp(active.pnl, 0)
    return {
        "test": label,
        "active_days": len(active),
        "hit_rate": (active.pnl > 0).mean(),
        "mean_pnl_per_bbl": active.pnl.mean(),
        "total_pnl_per_bbl": active.pnl.sum(),
        "t_stat": test.statistic,
        "p_value": test.pvalue,
    }
