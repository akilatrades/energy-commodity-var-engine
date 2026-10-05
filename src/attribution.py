"""Parametric VaR attribution for a linear portfolio."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def component_var(
    position_pnl: pd.DataFrame,
    confidence: float = 0.99,
) -> pd.DataFrame:
    """Calculate marginal and component VaR under a zero-mean normal model.

    For a linear portfolio with covariance matrix Sigma and unit exposure to
    each position-P&L series, portfolio sigma is sqrt(1' Sigma 1). Component
    VaR is z * Cov(P&L_i, P&L_portfolio) / sigma_portfolio.

    Components sum to total parametric VaR (up to floating-point tolerance).
    """
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")
    if position_pnl.empty:
        raise ValueError("position_pnl cannot be empty.")

    cols = [c for c in position_pnl.columns if c != "portfolio_pnl"]
    x = position_pnl[cols].dropna(how="any").astype(float)
    cov = x.cov().values
    ones = np.ones(len(cols))
    portfolio_var = float(ones @ cov @ ones)
    if portfolio_var <= 0:
        raise ValueError("Portfolio variance must be positive.")

    portfolio_sigma = float(np.sqrt(portfolio_var))
    z = float(norm.ppf(confidence))
    cov_with_port = cov @ ones
    marginal = z * cov_with_port / portfolio_sigma
    component = marginal * ones
    total = z * portfolio_sigma

    out = pd.DataFrame(
        {
            "symbol": cols,
            "marginal_var": marginal,
            "component_var": component,
        }
    )
    out["pct_of_total_var"] = out["component_var"] / total
    out["diversifier"] = out["component_var"] < 0
    out = out.sort_values("component_var", ascending=False).reset_index(drop=True)
    return out
