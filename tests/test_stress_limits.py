import pandas as pd

from src.limits import limit_status
from src.portfolio import FuturesPosition
from src.stress import run_stress_scenarios


def test_stress_and_limits():
    pos = [FuturesPosition("CL=F", "WTI", 1, 1_000)]
    latest = pd.Series({"CL=F": 80.0})
    out = run_stress_scenarios(latest, pos, {"down": {"CL=F": -0.10}})
    assert out["portfolio_stress_pnl"].iloc[0] == -8_000
    assert limit_status(90, 100)["status"] == "WATCH"
    assert limit_status(101, 100)["status"] == "BREACH"
