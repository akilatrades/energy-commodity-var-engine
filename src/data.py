"""Market-data loading, validation, and deterministic demo-data generation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_SYMBOLS = ["CL=F", "RB=F", "HO=F", "NG=F"]


def download_yahoo_prices(
    symbols: list[str] | None = None,
    start: str = "2018-01-01",
    end: str | None = None,
) -> pd.DataFrame:
    """Download aligned daily close prices for public continuous futures proxies."""
    import yfinance as yf

    symbols = symbols or DEFAULT_SYMBOLS
    raw = yf.download(
        symbols,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )
    if raw.empty:
        raise ValueError("Yahoo Finance returned no data.")

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].copy()
    else:
        close = raw[["Close"]].rename(columns={"Close": symbols[0]})

    close = close.reindex(columns=symbols).sort_index().dropna(how="any")
    validate_price_history(close)
    return close.astype(float)


def validate_price_history(prices: pd.DataFrame, min_observations: int = 300) -> None:
    """Apply basic market-data quality checks before risk calculations."""
    if prices.empty:
        raise ValueError("Price history is empty.")
    if len(prices) < min_observations:
        raise ValueError(
            f"At least {min_observations} aligned observations are required; got {len(prices)}."
        )
    if prices.index.has_duplicates:
        raise ValueError("Price history contains duplicate dates.")
    if not prices.index.is_monotonic_increasing:
        raise ValueError("Price history must be sorted in ascending date order.")
    if prices.isna().any().any():
        raise ValueError("Price history contains missing values after alignment.")
    if not np.isfinite(prices.to_numpy(dtype=float)).all():
        raise ValueError("Price history contains non-finite values.")


def make_demo_prices(n_days: int = 1_500, seed: int = 42) -> pd.DataFrame:
    """Generate deterministic correlated energy price paths for offline tests."""
    if n_days < 300:
        raise ValueError("n_days must be at least 300.")

    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-02", periods=n_days)
    corr = np.array(
        [
            [1.00, 0.72, 0.68, 0.28],
            [0.72, 1.00, 0.76, 0.22],
            [0.68, 0.76, 1.00, 0.20],
            [0.28, 0.22, 0.20, 1.00],
        ]
    )
    vols = np.array([0.025, 0.027, 0.026, 0.040])
    cov = np.outer(vols, vols) * corr

    innovations = rng.multivariate_normal(np.zeros(4), cov, size=n_days)
    volatility_state = np.empty(n_days)
    volatility_state[0] = 1.0
    for i in range(1, n_days):
        volatility_state[i] = 0.92 * volatility_state[i - 1] + 0.08 * (
            0.75 + 0.75 * abs(rng.normal())
        )

    log_returns = innovations * volatility_state[:, None]
    starts = np.array([70.0, 2.15, 2.35, 3.25])
    prices = starts * np.exp(np.cumsum(log_returns, axis=0))

    out = pd.DataFrame(prices, index=dates, columns=DEFAULT_SYMBOLS)
    validate_price_history(out)
    return out


def save_price_snapshot(prices: pd.DataFrame, path: str | Path) -> None:
    """Save the exact aligned price sample used by an analysis run."""
    out = prices.copy()
    out.index.name = "date"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path)
