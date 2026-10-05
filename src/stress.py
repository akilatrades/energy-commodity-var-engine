"""Deterministic stress testing for the illustrative energy book."""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from src.portfolio import FuturesPosition


DEFAULT_STRESSES: dict[str, dict[str, float]] = {
    "Broad energy selloff": {"CL=F": -0.20, "RB=F": -0.18, "HO=F": -0.17, "NG=F": -0.25},
    "Crude rally / products lag": {"CL=F": 0.20, "RB=F": 0.10, "HO=F": 0.08, "NG=F": 0.05},
    "Refined-products squeeze": {"CL=F": 0.05, "RB=F": 0.22, "HO=F": 0.18, "NG=F": 0.00},
    "Natural-gas shock": {"CL=F": 0.00, "RB=F": 0.00, "HO=F": 0.00, "NG=F": 0.35},
}


def run_stress_scenarios(
    latest_prices: pd.Series,
    positions: list[FuturesPosition],
    scenarios: Mapping[str, Mapping[str, float]] | None = None,
) -> pd.DataFrame:
    """Apply percentage price shocks and calculate linear futures P&L."""
    scenarios = scenarios or DEFAULT_STRESSES
    rows = []

    for scenario_name, shocks in scenarios.items():
        total = 0.0
        row: dict[str, float | str] = {"scenario": scenario_name}
        for p in positions:
            if p.symbol not in latest_prices.index:
                raise ValueError(f"Missing latest price for {p.symbol}.")
            shock = float(shocks.get(p.symbol, 0.0))
            price_change = float(latest_prices[p.symbol]) * shock
            pnl = p.contracts * p.contract_multiplier * price_change
            row[f"{p.symbol}_shock_pct"] = shock
            row[f"{p.symbol}_pnl"] = pnl
            total += pnl
        row["portfolio_stress_pnl"] = total
        rows.append(row)

    return pd.DataFrame(rows)
