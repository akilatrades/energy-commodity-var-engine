"""Full revaluation of European option legs plus linear futures on one factor."""

from dataclasses import dataclass

import numpy as np

from src.option_pricing import black76


@dataclass(frozen=True)
class OptionLeg:
    kind: str
    strike: float
    quantity: float  # signed barrels, not contracts
    maturity: float  # years
    volatility: float


def full_revaluation_pnl(
    forward,
    changes,
    legs,
    futures_barrels=0.0,
    rate=0.0,
    horizon_years=1 / 252,
    volatility_shift=0.0,
):
    """Hold today's book fixed, age each leg and mark under every price shock.

    Constant-vol historical scenarios by default. Optional absolute volatility
    shift is a stress, not a calibrated joint price/volatility distribution.
    Reject nonpositive shocked futures instead of silently clipping them.
    """
    changes = np.asarray(changes, dtype=float)
    if changes.ndim != 1 or not np.isfinite(changes).all():
        raise ValueError("changes must be a finite one-dimensional array")
    if (
        not np.isfinite(
            [forward, rate, futures_barrels, horizon_years, volatility_shift]
        ).all()
        or forward <= 0
        or horizon_years < 0
    ):
        raise ValueError("Invalid market inputs")
    if np.any(forward + changes <= 0):
        raise ValueError(
            "Black-76 cannot revalue nonpositive futures; use a normal/shifted model"
        )
    pnl = futures_barrels * changes.copy()
    for leg in legs:
        if not np.isfinite(leg.quantity) or leg.volatility + volatility_shift < 0:
            raise ValueError("Invalid option quantity or shocked volatility")
        if leg.maturity < horizon_years:
            raise ValueError("Horizon beyond expiry needs a settlement path")
        initial = black76(
            forward, leg.strike, leg.maturity, leg.volatility, rate, leg.kind
        )
        values = np.array(
            [
                black76(
                    float(f),
                    leg.strike,
                    leg.maturity - horizon_years,
                    leg.volatility + volatility_shift,
                    rate,
                    leg.kind,
                )
                for f in forward + changes
            ]
        )
        pnl += leg.quantity * (values - initial)
    return pnl
