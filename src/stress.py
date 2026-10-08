"""Hypothetical and historical stress testing."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.portfolio import FuturesPosition, pnl_history_from_prices


def load_stress_scenarios(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "scenario" not in frame.columns or frame.empty:
        raise ValueError(
            "Stress scenario file must contain a scenario column and rows."
        )
    return frame


def run_hypothetical_scenarios(
    latest_prices: pd.Series,
    positions: list[FuturesPosition],
    scenarios: pd.DataFrame,
) -> pd.DataFrame:
    """Apply configured percentage shocks to current portfolio sensitivities."""
    rows: list[dict] = []

    for _, scenario in scenarios.iterrows():
        row = {
            "scenario": str(scenario["scenario"]),
            "source_type": "hypothetical",
        }
        total = 0.0

        for p in positions:
            if p.symbol not in latest_prices.index:
                raise ValueError(f"Missing latest price for {p.symbol}.")
            if p.symbol not in scenarios.columns:
                raise ValueError(f"Stress scenario file is missing {p.symbol}.")

            shock = float(scenario[p.symbol])
            price_change = float(latest_prices[p.symbol]) * shock
            position_pnl = p.contracts * p.contract_multiplier * price_change
            row[f"{p.symbol}_shock_pct"] = shock
            row[f"{p.symbol}_pnl"] = position_pnl
            total += position_pnl

        row["portfolio_stress_pnl"] = total
        rows.append(row)

    return pd.DataFrame(rows)


def historical_replay_scenarios(
    prices: pd.DataFrame,
    positions: list[FuturesPosition],
    count: int = 5,
) -> pd.DataFrame:
    """Return the worst observed fixed-book P&L days and realized price changes."""
    if count <= 0:
        raise ValueError("count must be positive.")

    symbols = [p.symbol for p in positions]
    changes = prices[symbols].diff().dropna(how="any")
    pnl = pnl_history_from_prices(prices, positions)
    worst_dates = pnl["portfolio_pnl"].nsmallest(min(count, len(pnl))).index

    rows: list[dict] = []
    for date in worst_dates:
        row = {
            "scenario": f"Historical replay {pd.Timestamp(date).date()}",
            "source_type": "historical_replay",
            "source_date": pd.Timestamp(date).date().isoformat(),
        }
        for p in positions:
            row[f"{p.symbol}_price_change"] = float(changes.loc[date, p.symbol])
            row[f"{p.symbol}_pnl"] = float(pnl.loc[date, p.symbol])
        row["portfolio_stress_pnl"] = float(pnl.loc[date, "portfolio_pnl"])
        rows.append(row)

    return pd.DataFrame(rows)
