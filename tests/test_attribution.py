import numpy as np
import pandas as pd
from scipy.stats import norm

from src.attribution import component_var


def test_component_var_sums_to_total_parametric_var():
    rng = np.random.default_rng(4)
    x = pd.DataFrame(
        {
            "A": rng.normal(0, 100, 500),
            "B": rng.normal(0, 50, 500),
        }
    )
    x["portfolio_pnl"] = x.sum(axis=1)
    comp = component_var(x, 0.99)
    total = norm.ppf(0.99) * x[["A", "B"]].sum(axis=1).std(ddof=1)
    assert np.isclose(comp["component_var"].sum(), total, rtol=1e-10)
