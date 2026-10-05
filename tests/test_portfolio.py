import pandas as pd

from src.portfolio import FuturesPosition, pnl_history_from_prices


def test_linear_futures_pnl():
    prices = pd.DataFrame(
        {"CL=F": [70.0, 71.0, 69.0]},
        index=pd.date_range("2026-01-01", periods=3),
    )
    positions = [FuturesPosition("CL=F", "WTI", 2, 1_000)]
    pnl = pnl_history_from_prices(prices, positions)
    assert pnl["CL=F"].iloc[0] == 2_000
    assert pnl["CL=F"].iloc[1] == -4_000
    assert (pnl["portfolio_pnl"] == pnl["CL=F"]).all()
