import pandas as pd

from src.limits import limit_status
from src.portfolio import FuturesPosition
from src.stress import historical_replay_scenarios, run_hypothetical_scenarios


def test_hypothetical_stress_and_limits():
    positions = [FuturesPosition("CL=F", "WTI", 1, 1_000)]
    latest = pd.Series({"CL=F": 80.0})
    scenarios = pd.DataFrame({"scenario": ["down"], "CL=F": [-0.10]})
    result = run_hypothetical_scenarios(latest, positions, scenarios)
    assert result["portfolio_stress_pnl"].iloc[0] == -8_000
    assert limit_status(90, 100)["status"] == "WATCH"
    assert limit_status(101, 100)["status"] == "BREACH"


def test_historical_replay_returns_worst_days():
    dates = pd.bdate_range("2026-01-01", periods=6)
    prices = pd.DataFrame({"CL=F": [70, 71, 68, 69, 65, 66]}, index=dates)
    positions = [FuturesPosition("CL=F", "WTI", 1, 1_000)]
    result = historical_replay_scenarios(prices, positions, count=2)
    assert len(result) == 2
    assert result["source_type"].eq("historical_replay").all()
    assert result["portfolio_stress_pnl"].iloc[0] <= result["portfolio_stress_pnl"].iloc[1]
