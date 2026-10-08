"""European options on positive futures prices; premiums in dollars per barrel.

Black-76 is an approximation for European terminal-settled structures, not an
American option or a monthly average-price swap/collar pricing model.
"""

from math import exp, isfinite, log, sqrt

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm


def black76(forward, strike, maturity, volatility, rate=0.0, kind="call"):
    if kind not in {"call", "put"}:
        raise ValueError("kind must be call or put")
    if not all(isfinite(x) for x in (forward, strike, maturity, volatility, rate)):
        raise ValueError("Inputs must be finite")
    if forward <= 0 or strike <= 0 or maturity < 0 or volatility < 0:
        raise ValueError("Positive forward/strike and nonnegative time/vol required")
    sign = 1 if kind == "call" else -1
    discount = exp(-rate * maturity)
    if maturity == 0 or volatility == 0:
        return discount * max(sign * (forward - strike), 0.0)
    st = volatility * sqrt(maturity)
    d1 = log(forward / strike) / st + st / 2
    d2 = d1 - st
    return float(
        discount * sign * (forward * norm.cdf(sign * d1) - strike * norm.cdf(sign * d2))
    )


def costless_ceiling(forward, floor, maturity, volatility, rate=0.0, subfloor=None):
    """Solve call premium = bought put premium minus optional sold put premium."""
    if maturity <= 0 or volatility <= 0 or not 0 < floor < forward:
        raise ValueError("Require positive time/vol and 0 < floor < forward")
    target = black76(forward, floor, maturity, volatility, rate, "put")
    if subfloor is not None:
        if not 0 < subfloor < floor:
            raise ValueError("Require 0 < subfloor < floor")
        target -= black76(forward, subfloor, maturity, volatility, rate, "put")

    def objective(k):
        return black76(forward, k, maturity, volatility, rate, "call") - target

    upper = forward * 2
    while objective(upper) > 0 and upper < forward * 1e6:
        upper *= 2
    if target <= 1e-12 or objective(upper) > 0:
        raise ValueError("No numerically meaningful finite costless ceiling")
    return float(brentq(objective, forward, upper))


def producer_revenues(
    terminal,
    basis,
    forward,
    floor,
    ceiling,
    three_way_ceiling,
    subfloor,
    barrels=100_000,
    hedge_fraction=1.0,
):
    """Expiry revenues. Swap and futures use the same terminal reference.

    Zero net premiums assumed for collars solved at inception. Interim margin,
    credit, volume uncertainty and settlement averaging are outside this payoff.
    Terminal prices may be negative: intrinsic payoffs still remain valid.
    """
    if not 0 <= hedge_fraction <= 1 or barrels <= 0:
        raise ValueError("Invalid volume or hedge fraction")
    if not 0 < subfloor < floor < forward < min(ceiling, three_way_ceiling):
        raise ValueError("Invalid strike ordering")
    s, b = np.broadcast_arrays(np.asarray(terminal, float), np.asarray(basis, float))
    if not np.isfinite(s).all() or not np.isfinite(b).all():
        raise ValueError("Terminal prices and basis must be finite")
    physical = s + b
    put = np.maximum(floor - s, 0)
    collar = put - np.maximum(s - ceiling, 0)
    three = put - np.maximum(subfloor - s, 0) - np.maximum(s - three_way_ceiling, 0)
    return {
        "unhedged": barrels * physical,
        "futures": barrels * (physical + hedge_fraction * (forward - s)),
        "fixed_price_swap": barrels * (physical + hedge_fraction * (forward - s)),
        "costless_collar": barrels * (physical + hedge_fraction * collar),
        "three_way_collar": barrels * (physical + hedge_fraction * three),
    }
