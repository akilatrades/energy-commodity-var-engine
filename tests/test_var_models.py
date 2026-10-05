import numpy as np
import pandas as pd

from src.data import make_demo_prices
from src.portfolio import FuturesPosition
from src.var_models import (
    historical_es,
    historical_var,
    monte_carlo_factor_var_es,
    parametric_var,
    weighted_historical_es,
    weighted_historical_var,
)


def test_var_and_es_are_positive():
    pnl = pd.Series([-100, -50, 20, 30, -10, 40] * 20, dtype=float)
    assert historical_var(pnl, 0.95) >= 0
    assert historical_es(pnl, 0.95) >= historical_var(pnl, 0.95)
    assert weighted_historical_var(pnl, 0.95, 0.97) >= 0
    assert weighted_historical_es(pnl, 0.95, 0.97) >= 0


def test_parametric_var_positive():
    rng = np.random.default_rng(1)
    pnl = pd.Series(rng.normal(0, 100, 600))
    assert parametric_var(pnl, 0.99) > 0


def test_factor_monte_carlo_runs_on_correlated_prices():
    prices = make_demo_prices(600)
    positions = [
        FuturesPosition("CL=F", "WTI", 2, 1_000),
        FuturesPosition("RB=F", "RBOB", -1, 42_000),
        FuturesPosition("HO=F", "Heating Oil", -1, 42_000),
        FuturesPosition("NG=F", "Natural Gas", 2, 10_000),
    ]
    var, es = monte_carlo_factor_var_es(
        prices,
        positions,
        confidence=0.99,
        n_sims=5_000,
        degrees_of_freedom=6,
    )
    assert var > 0
    assert es >= var
