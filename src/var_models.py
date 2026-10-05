"""Value at Risk and Expected Shortfall models."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

from src.portfolio import FuturesPosition


def _clean_pnl(pnl: pd.Series) -> pd.Series:
    out = pd.Series(pnl, copy=True).dropna().astype(float)
    if len(out) < 20:
        raise ValueError("At least 20 P&L observations are required.")
    return out


def historical_var(pnl: pd.Series, confidence: float = 0.99) -> float:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")
    x = _clean_pnl(pnl)
    return float(max(-x.quantile(1 - confidence), 0.0))


def historical_es(pnl: pd.Series, confidence: float = 0.99) -> float:
    x = _clean_pnl(pnl)
    var = historical_var(x, confidence)
    tail = x[x <= -var]
    return float(max(-tail.mean(), 0.0)) if not tail.empty else 0.0


def parametric_var(
    pnl: pd.Series,
    confidence: float = 0.99,
    mean_adjusted: bool = False,
) -> float:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")
    x = _clean_pnl(pnl)
    mu = float(x.mean()) if mean_adjusted else 0.0
    sigma = float(x.std(ddof=1))
    lower_quantile = mu + sigma * norm.ppf(1 - confidence)
    return float(max(-lower_quantile, 0.0))


def parametric_es(
    pnl: pd.Series,
    confidence: float = 0.99,
    mean_adjusted: bool = False,
) -> float:
    x = _clean_pnl(pnl)
    mu = float(x.mean()) if mean_adjusted else 0.0
    sigma = float(x.std(ddof=1))
    z_left = norm.ppf(1 - confidence)
    left_tail_mean = mu - sigma * norm.pdf(z_left) / (1 - confidence)
    return float(max(-left_tail_mean, 0.0))


def ewma_weights(n: int, decay: float = 0.97) -> np.ndarray:
    if n <= 0:
        raise ValueError("n must be positive.")
    if not 0 < decay < 1:
        raise ValueError("decay must be between 0 and 1.")
    powers = np.arange(n - 1, -1, -1)
    weights = (1 - decay) * np.power(decay, powers)
    return weights / weights.sum()


def weighted_historical_var(
    pnl: pd.Series,
    confidence: float = 0.99,
    decay: float = 0.97,
) -> float:
    x = _clean_pnl(pnl)
    weights = ewma_weights(len(x), decay)
    order = np.argsort(x.values)
    sorted_pnl = x.values[order]
    sorted_weights = weights[order]
    cumulative = np.cumsum(sorted_weights)
    idx = int(np.searchsorted(cumulative, 1 - confidence, side="left"))
    idx = min(max(idx, 0), len(sorted_pnl) - 1)
    return float(max(-sorted_pnl[idx], 0.0))


def weighted_historical_es(
    pnl: pd.Series,
    confidence: float = 0.99,
    decay: float = 0.97,
) -> float:
    """Probability-weighted Expected Shortfall for the weighted historical model."""
    x = _clean_pnl(pnl)
    weights = ewma_weights(len(x), decay)
    order = np.argsort(x.values)
    sorted_pnl = x.values[order]
    sorted_weights = weights[order]

    tail_probability = 1 - confidence
    remaining = tail_probability
    weighted_loss = 0.0

    for value, weight in zip(sorted_pnl, sorted_weights):
        if remaining <= 0:
            break
        used = min(float(weight), remaining)
        weighted_loss += used * (-float(value))
        remaining -= used

    return float(max(weighted_loss / tail_probability, 0.0))


def monte_carlo_factor_var_es(
    prices: pd.DataFrame,
    positions: list[FuturesPosition],
    confidence: float = 0.99,
    n_sims: int = 50_000,
    degrees_of_freedom: int = 6,
    seed: int = 42,
) -> tuple[float, float]:
    """Simulate correlated Student-t futures price changes and revalue the book.

    Absolute price changes are used rather than percentage returns because
    futures prices can cross or approach zero and because historical position
    P&L is calculated directly from settlement-price changes.
    """
    if n_sims <= 0:
        raise ValueError("n_sims must be positive.")
    if degrees_of_freedom <= 2:
        raise ValueError("degrees_of_freedom must be greater than 2.")

    symbols = [p.symbol for p in positions]
    changes = prices[symbols].diff().dropna(how="any").astype(float)
    if len(changes) < 20:
        raise ValueError("At least 20 price-change observations are required.")

    covariance = changes.cov().values
    scale = covariance * (degrees_of_freedom - 2) / degrees_of_freedom
    rng = np.random.default_rng(seed)

    normal_draws = rng.multivariate_normal(
        np.zeros(len(symbols)),
        scale,
        size=n_sims,
        check_valid="ignore",
    )
    chi = rng.chisquare(degrees_of_freedom, size=n_sims) / degrees_of_freedom
    simulated_changes = normal_draws / np.sqrt(chi)[:, None]

    unit_exposures = np.array(
        [p.contracts * p.contract_multiplier for p in positions],
        dtype=float,
    )
    simulated_pnl = simulated_changes @ unit_exposures

    cutoff = float(np.quantile(simulated_pnl, 1 - confidence))
    var = max(-cutoff, 0.0)
    tail = simulated_pnl[simulated_pnl <= cutoff]
    es = max(-float(tail.mean()), 0.0) if len(tail) else 0.0
    return float(var), float(es)


def summarize_var_methods(
    pnl: pd.Series,
    prices: pd.DataFrame,
    positions: list[FuturesPosition],
    confidence: float = 0.99,
    decay: float = 0.97,
    n_sims: int = 50_000,
    monte_carlo_df: int = 6,
    mean_adjusted: bool = False,
) -> pd.DataFrame:
    mc_var, mc_es = monte_carlo_factor_var_es(
        prices,
        positions,
        confidence=confidence,
        n_sims=n_sims,
        degrees_of_freedom=monte_carlo_df,
    )

    rows = [
        {
            "method": "Historical",
            "confidence": confidence,
            "var": historical_var(pnl, confidence),
            "expected_shortfall": historical_es(pnl, confidence),
        },
        {
            "method": "Parametric Normal",
            "confidence": confidence,
            "var": parametric_var(pnl, confidence, mean_adjusted),
            "expected_shortfall": parametric_es(pnl, confidence, mean_adjusted),
        },
        {
            "method": f"Monte Carlo Student-t (df={monte_carlo_df})",
            "confidence": confidence,
            "var": mc_var,
            "expected_shortfall": mc_es,
        },
        {
            "method": f"Weighted Historical (lambda={decay:.2f})",
            "confidence": confidence,
            "var": weighted_historical_var(pnl, confidence, decay),
            "expected_shortfall": weighted_historical_es(pnl, confidence, decay),
        },
    ]
    return pd.DataFrame(rows)
