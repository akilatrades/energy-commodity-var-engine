"""Predictable EWMA scaling of portfolio P&L for filtered historical VaR.

At t, sigma_t uses only observations before t. Historical shocks are divided
by their own prior-day volatility, then multiplied by sigma_t. No future
realization enters a forecast. This is a fixed-book, one-factor P&L filter.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def ewma_prior_volatility(
    pnl: pd.Series, decay: float = 0.94, warmup: int = 60
) -> pd.Series:
    """Use a past-only warmup second moment; do not publish warmup residuals."""
    x = pd.Series(pnl, copy=True).astype(float)
    if not 0 < decay < 1 or warmup < 2 or len(x) <= warmup:
        raise ValueError("Invalid EWMA decay, warmup or sample length")
    if x.index.has_duplicates or not x.index.is_monotonic_increasing:
        raise ValueError("P&L dates must be unique and increasing")
    if not np.isfinite(x).all():
        raise ValueError("P&L must be finite and complete")
    variance = float(np.mean(np.square(x.iloc[:warmup])))
    if variance <= 0:
        raise ValueError("Warmup needs positive variance")
    sigma = pd.Series(np.nan, index=x.index, name="prior_sigma")
    for i in range(warmup, len(x)):
        sigma.iloc[i] = np.sqrt(variance)
        variance = decay * variance + (1 - decay) * float(x.iloc[i]) ** 2
    return sigma


def month_turn_flags(
    dates: pd.DatetimeIndex, first: int = 3, last: int = 2
) -> pd.Series:
    """First/last Monday-Friday weekdays, not exchange sessions or known rolls.

    Uses calendar month bounds, never the observed sample's end; holidays are
    not removed. This flag can be computed ex ante and is only a heuristic.
    """
    dates = pd.DatetimeIndex(dates)
    if first < 0 or last < 0:
        raise ValueError("Calendar bands cannot be negative")
    flags = []
    for date in dates:
        day = np.datetime64(date.date(), "D")
        start = np.datetime64(date.to_period("M").start_time.date(), "D")
        end = np.datetime64((date.to_period("M") + 1).start_time.date(), "D")
        from_start = np.busday_count(start, day) + int(np.is_busday(day))
        to_end = np.busday_count(day, end)
        flags.append(bool(from_start <= first or to_end <= last))
    return pd.Series(flags, index=dates, name="possible_roll_calendar_flag")


def filtered_forecasts(
    pnl: pd.Series,
    window: int = 250,
    confidence: float = 0.99,
    decay: float = 0.94,
    warmup: int = 60,
    filtered: bool = True,
    exclude_training_flags: pd.Series | None = None,
) -> pd.DataFrame:
    """Estimate from previous window dates and score ALL subsequent losses.

    Calendar exclusion is a sensitivity, not repaired prices. Both filtered
    and raw variants start after the same warmup/window for fair comparison.
    """
    x = pd.Series(pnl, copy=True).astype(float)
    if not 0 < confidence < 1 or window < 20 or len(x) <= window + warmup:
        raise ValueError("Invalid confidence/window or insufficient history")
    sigma = ewma_prior_volatility(x, decay, warmup)
    residuals = x / sigma if filtered else x
    flags = pd.Series(False, index=x.index)
    if exclude_training_flags is not None:
        flags = exclude_training_flags.reindex(x.index)
        if flags.isna().any():
            raise ValueError("Training flags must cover every P&L date")
        flags = flags.astype(bool)
    name = "ewma_fhs" if filtered else "historical_common"
    if exclude_training_flags is not None:
        name += "_exclude_calendar_training"
    rows = []
    for i in range(window + warmup, len(x)):
        train = residuals.iloc[i - window : i]
        train = train[~flags.iloc[i - window : i]]
        if len(train) < 20 or train.isna().any():
            raise ValueError("Insufficient standardized training shocks")
        scenarios = train * float(sigma.iloc[i]) if filtered else train
        cutoff = float(scenarios.quantile(1 - confidence))
        var = max(-cutoff, 0.0)
        tail = scenarios[scenarios <= cutoff]
        rows.append(
            dict(
                date=x.index[i],
                method=name,
                window=window,
                decay=decay if filtered else None,
                realized_pnl=float(x.iloc[i]),
                var=var,
                expected_shortfall=max(-float(tail.mean()), 0.0),
                exception=bool(x.iloc[i] < -var),
                training_shocks=len(train),
                prior_sigma=float(sigma.iloc[i]),
            )
        )
    return pd.DataFrame(rows).set_index("date")
