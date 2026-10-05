import numpy as np
import pandas as pd

from src.var_models import (
    historical_es,
    historical_var,
    parametric_var,
    summarize_var_methods,
    weighted_historical_var,
)


def test_var_is_positive_and_es_is_not_smaller_than_var():
    pnl = pd.Series([-100, -50, 20, 30, -10, 40] * 20, dtype=float)
    var = historical_var(pnl, 0.95)
    es = historical_es(pnl, 0.95)
    assert var >= 0
    assert es >= var


def test_parametric_var_and_summary():
    rng = np.random.default_rng(1)
    pnl = pd.Series(rng.normal(0, 100, 600))
    assert parametric_var(pnl, 0.99) > 0
    assert weighted_historical_var(pnl, 0.99) > 0
    out = summarize_var_methods(pnl, 0.99, n_sims=2_000)
    assert set(out["method"]) >= {"Historical", "Parametric Normal", "Monte Carlo Normal"}
