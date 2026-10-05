"""Portfolio definitions and linear futures P&L calculations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class FuturesPosition:
    symbol: str
    name: str
    contracts: int
    contract_multiplier: float
    currency: str = "USD"


def load_positions_csv(path: str | Path) -> list[FuturesPosition]:
    """Load auditable position assumptions from CSV."""
    frame = pd.read_csv(path)
    required = {"symbol", "name", "contracts", "contract_multiplier", "currency"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Position file is missing columns: {sorted(missing)}")

    positions = [
        FuturesPosition(
            symbol=str(row.symbol),
            name=str(row.name),
            contracts=int(row.contracts),
            contract_multiplier=float(row.contract_multiplier),
            currency=str(row.currency),
        )
        for row in frame.itertuples(index=False)
    ]
    if not positions:
        raise ValueError("Position file contains no positions.")
    return positions


def positions_to_frame(positions: Iterable[FuturesPosition]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "symbol": p.symbol,
                "name": p.name,
                "contracts": p.contracts,
                "contract_multiplier": p.contract_multiplier,
                "currency": p.currency,
            }
            for p in positions
        ]
    )


def position_notionals(
    positions: Iterable[FuturesPosition],
    latest_prices: pd.Series,
) -> pd.Series:
    """Return signed current notionals by symbol."""
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
    """Calculate exact daily P&L for fixed linear futures positions."""
    positions = list(positions)
    symbols = [p.symbol for p in positions]
    missing = sorted(set(symbols).difference(prices.columns))
    if missing:
        raise ValueError(f"Missing price columns: {missing}")

    changes = prices[symbols].sort_index().diff().dropna(how="any")
    pnl = pd.DataFrame(index=changes.index)

    for p in positions:
        pnl[p.symbol] = changes[p.symbol] * p.contract_multiplier * p.contracts

    pnl["portfolio_pnl"] = pnl.sum(axis=1)
    return pnl
