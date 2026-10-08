"""Build an additive continuous futures series from explicit contract settlements.

Selection is supplied in advance. On each date, mark yesterday's held contract
to today's settlement, then switch at that same settlement if scheduled.
"""
import numpy as np
import pandas as pd


def build_continuous(settlements: pd.DataFrame, schedule: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "contract", "settlement"}
    if not required <= set(settlements) or not {"date","contract"} <= set(schedule):
        raise ValueError("Expected date/contract/settlement panel and date/contract schedule")
    p, s = settlements.copy(), schedule.copy()
    p["date"], s["date"] = pd.to_datetime(p.date), pd.to_datetime(s.date)
    if p[list(required)].isna().any().any() or s[["date","contract"]].isna().any().any():
        raise ValueError("Missing contract panel or schedule fields")
    if p.duplicated(["date","contract"]).any() or s.date.duplicated().any():
        raise ValueError("Duplicate contract settlements or schedule dates")
    p["settlement"] = pd.to_numeric(p.settlement)
    if not np.isfinite(p.settlement).all(): raise ValueError("Nonfinite settlement")
    s = s.sort_values("date").set_index("date")
    if len(s) < 2: raise ValueError("Need at least two scheduled dates")
    if set(p.date) != set(s.index):
        raise ValueError("Schedule must cover every panel date exactly once")
    panel = p.set_index(["date","contract"]).settlement
    rows=[]; previous_contract=None; previous_price=None
    for date, row in s.iterrows():
        contract=row.contract
        try:
            new=float(panel.loc[(date,contract)])
            old=new if previous_contract is None else float(panel.loc[(date,previous_contract)])
        except KeyError as exc:
            raise ValueError(f"Missing selected or outgoing contract settlement on {date}") from exc
        gap=new-old
        rows.append(dict(date=date,contract=contract,raw=new,roll_gap=gap,
                         held_contract_pnl=np.nan if previous_price is None else old-previous_price))
        previous_contract,previous_price=contract,new
    out=pd.DataFrame(rows).set_index("date")
    cumulative=out.roll_gap.cumsum()
    # Anchor adjusted history to the final observed settlement. Only differences
    # are suitable for P&L: adjusted levels can be negative and revise on rolls.
    out["adjusted"]=out.raw-cumulative+cumulative.iloc[-1]
    out["raw_change"]=out.raw.diff()
    out["adjusted_change"]=out.adjusted.diff()
    if not np.allclose(out.adjusted_change.iloc[1:],out.held_contract_pnl.iloc[1:]):
        raise AssertionError("Adjusted P&L does not reconcile to held contract")
    return out
