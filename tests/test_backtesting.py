import numpy as np
import pandas as pd

from src.backtesting import calibration_sensitivity, compare_backtests


def test_model_comparison_and_sensitivity():
    rng = np.random.default_rng(8)
    pnl = pd.Series(
        rng.normal(0, 100, 900),
        index=pd.bdate_range("2023-01-02", periods=900),
    )
    summary, forecasts = compare_backtests(
        pnl,
        methods=["historical", "parametric", "weighted_historical"],
        window=250,
        confidence=0.99,
        decay=0.97,
    )
    assert set(summary["method"]) == {
        "historical",
        "parametric",
        "weighted_historical",
    }
    assert len(forecasts) == 3 * (900 - 250)
    assert summary["actual_exception_rate"].between(0, 1).all()

    sensitivity = calibration_sensitivity(
        pnl,
        windows=[125, 250, 500],
        confidence=0.99,
        decays=[0.94, 0.97],
    )
    assert set(sensitivity["window"]) == {125, 250, 500}
