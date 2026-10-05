"""Value at Risk and Expected Shortfall models for linear portfolios."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def _clean_pnl(pnl: pd.Series) -> pd.Series:
    out = pd.Series(pnl, copy=True).dropna().astype(float)
    if len(out) < 20:
        raise ValueError("At least 20 P&L observations are required.")
    return out


def historical_var(pnl: pd.Series, confidence: float = 0.99) -> float:
    """Historical VaR as a positive loss magnitude."""
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")
    x = _clean_pnl(pnl)
    return float(max(-x.quantile(1 - confidence), 0.0))


def historical_es(pnl: pd.Series, confidence: float = 0.99) -> float:
    """Historical Expected Shortfall as a positive loss magnitude."""
    x = _clean_pnl(pnl)
    var = historical_var(x, confidence)
    tail = x[x <= -var]
    return float(max(-tail.mean(), 0.0)) if not tail.empty else 0.0


def parametric_var(
    pnl: pd.Series,
    confidence: float = 0.99,
    mean_adjusted: bool = True,
) -> float:
    """Normal-theory VaR estimated directly from portfolio P&L history."""
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")
    x = _clean_pnl(pnl)
    mu = float(x.mean()) if mean_adjusted else 0.0
    sigma = float(x.std(ddof=1))
    q = mu + sigma * norm.ppf(1 - confidence)
    return float(max(-q, 0.0))


def parametric_es(
    pnl: pd.Series,
    confidence: float = 0.99,
    mean_adjusted: bool = True,
) -> float:
    """Normal-theory Expected Shortfall."""
    x = _clean_pnl(pnl)
    mu = float(x.mean()) if mean_adjusted else 0.0
    sigma = float(x.std(ddof=1))
    z = norm.ppf(1 - confidence)
    left_tail_mean = mu - sigma * norm.pdf(z) / (1 - confidence)
    return float(max(-left_tail_mean, 0.0))


def ewma_weights(n: int, decay: float = 0.97) -> np.ndarray:
    """Return normalized exponential weights with most weight on recent data."""
    if n <= 0:
        raise ValueError("n must be positive.")
    if not 0 < decay < 1:
        raise ValueError("decay must be between 0 and 1.")
    powers = np.arange(n - 1, -1, -1)
    w = (1 - decay) * np.power(decay, powers)
    return w / w.sum()


def weighted_historical_var(
    pnl: pd.Series,
    confidence: float = 0.99,
    decay: float = 0.97,
) -> float:
    """Exponentially weighted historical VaR.

    Unlike plain historical VaR, recent observations receive more probability
    mass. This is an educational implementation, not a production bank model.
    """
    x = _clean_pnl(pnl)
    weights = ewma_weights(len(x), decay)
    order = np.argsort(x.values)
    sorted_pnl = x.values[order]
    sorted_w = weights[order]
    cumulative = np.cumsum(sorted_w)
    idx = int(np.searchsorted(cumulative, 1 - confidence, side="left"))
    idx = min(max(idx, 0), len(sorted_pnl) - 1)
    return float(max(-sorted_pnl[idx], 0.0))


def monte_carlo_var_es(
    pnl: pd.Series,
    confidence: float = 0.99,
    n_sims: int = 50_000,
    seed: int = 42,
) -> tuple[float, float]:
    """Monte Carlo VaR/ES using a fitted normal P&L distribution."""
    if n_sims <= 0:
        raise ValueError("n_sims must be positive.")
    x = _clean_pnl(pnl)
    rng = np.random.default_rng(seed)
    sims = rng.normal(float(x.mean()), float(x.std(ddof=1)), n_sims)
    cutoff = float(np.quantile(sims, 1 - confidence))
    var = max(-cutoff, 0.0)
    tail = sims[sims <= cutoff]
    es = max(-float(tail.mean()), 0.0) if len(tail) else 0.0
    return float(var), float(es)


def summarize_var_methods(
    pnl: pd.Series,
    confidence: float = 0.99,
    decay: float = 0.97,
    n_sims: int = 50_000,
) -> pd.DataFrame:
    """Return a compact comparison of the main VaR methods."""
    mc_var, mc_es = monte_carlo_var_es(pnl, confidence, n_sims=n_sims)
    rows = [
        {
            "method": "Historical",
            "var": historical_var(pnl, confidence),
            "expected_shortfall": historical_es(pnl, confidence),
        },
        {
            "method": "Parametric Normal",
            "var": parametric_var(pnl, confidence),
            "expected_shortfall": parametric_es(pnl, confidence),
        },
        {
            "method": "Monte Carlo Normal",
            "var": mc_var,
            "expected_shortfall": mc_es,
        },
        {
            "method": f"Weighted Historical (lambda={decay:.2f})",
            "var": weighted_historical_var(pnl, confidence, decay),
            "expected_shortfall": np.nan,
        },
    ]
    out = pd.DataFrame(rows)
    out.insert(1, "confidence", confidence)
    return out
