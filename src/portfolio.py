"""Portfolio definitions and linear futures P&L helpers.

This project treats futures positions as linear exposures. For a small daily
price move, the position P&L is approximated as:

    P&L = contracts * contract_multiplier * price_change

where contract_multiplier is in physical units per contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class FuturesPosition:
    """One linear futures position in an illustrative market-risk book."""

    symbol: str
    name: str
    contracts: int
    contract_multiplier: float
    currency: str = "USD"

    @property
    def direction(self) -> int:
        if self.contracts > 0:
            return 1
        if self.contracts < 0:
            return -1
        return 0


def default_energy_book() -> list[FuturesPosition]:
    """Return an illustrative diversified energy futures portfolio.

    Contract counts are examples for portfolio analytics only; they are not
    trade recommendations.
    """
    return [
        FuturesPosition("CL=F", "WTI Crude Oil", 40, 1_000),
        FuturesPosition("RB=F", "RBOB Gasoline", -15, 42_000),
        FuturesPosition("HO=F", "Heating Oil", -12, 42_000),
        FuturesPosition("NG=F", "Henry Hub Natural Gas", 35, 10_000),
    ]


def positions_to_frame(positions: Iterable[FuturesPosition]) -> pd.DataFrame:
    """Convert positions to a tabular representation."""
    rows = [
        {
            "symbol": p.symbol,
            "name": p.name,
            "contracts": p.contracts,
            "contract_multiplier": p.contract_multiplier,
            "currency": p.currency,
        }
        for p in positions
    ]
    return pd.DataFrame(rows)


def position_notionals(
    positions: Iterable[FuturesPosition],
    latest_prices: pd.Series,
) -> pd.Series:
    """Return signed current notionals for each position."""
    values: dict[str, float] = {}
    for p in positions:
        if p.symbol not in latest_prices.index:
            raise ValueError(f"Missing latest price for {p.symbol}.")
        values[p.symbol] = (
            p.contracts * p.contract_multiplier * float(latest_prices[p.symbol])
        )
    return pd.Series(values, name="signed_notional", dtype=float)


def pnl_history_from_prices(
    prices: pd.DataFrame,
    positions: Iterable[FuturesPosition],
) -> pd.DataFrame:
    """Calculate daily position and total P&L from aligned settlement prices.

    P&L uses first price differences, which is exact for a fixed number of
    linear futures contracts under the simplified contract-multiplier model.
    """
    positions = list(positions)
    needed = [p.symbol for p in positions]
    missing = sorted(set(needed).difference(prices.columns))
    if missing:
        raise ValueError(f"Missing price columns: {missing}")

    changes = prices[needed].sort_index().diff().dropna(how="any")
    pnl = pd.DataFrame(index=changes.index)

    for p in positions:
        pnl[p.symbol] = changes[p.symbol] * p.contract_multiplier * p.contracts

    pnl["portfolio_pnl"] = pnl.sum(axis=1)
    return pnl
