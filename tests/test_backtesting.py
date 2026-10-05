import numpy as np
import pandas as pd

from src.backtesting import rolling_var_forecasts, summarize_backtest


def test_backtest_outputs():
    rng = np.random.default_rng(8)
    pnl = pd.Series(rng.normal(0, 100, 700), index=pd.bdate_range("2023-01-02", periods=700))
    results = rolling_var_forecasts(pnl, window=250, confidence=0.99)
    summary = summarize_backtest(results, confidence=0.99)
    assert len(results) == 450
    assert 0 <= summary["actual_exception_rate"].iloc[0] <= 1
