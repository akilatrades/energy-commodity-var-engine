"""Exercise roll reconciliation on real, long-dated Yahoo closing prices.

This quarterly demonstration is NOT a reconstruction of Yahoo front-month rolls.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.continuous import build_continuous


def main():
    source = Path("outputs/contract_audit_2026-10/vendor_closes.csv.gz")
    out = Path("outputs/real_contract_roll_2026-10")
    out.mkdir(exist_ok=True)
    panel = pd.read_csv(source, parse_dates=["date"])
    wanted = [
        f"{root}{suffix}.NYM"
        for root in ["CL", "RB", "HO"]
        for suffix in ["X26", "Z26", "F27", "G27"]
    ]
    year = panel[
        panel.contract.isin(wanted)
        & (panel.date >= "2025-01-01")
        & (panel.date < "2026-01-01")
    ]
    wide = year.pivot(index="date", columns="contract", values="settlement").reindex(
        columns=wanted
    )
    missing = wide.isna().any(axis=1)
    wide.loc[missing].to_csv(out / "incomplete_quote_dates.csv")
    common_dates = wide.index[~missing]
    # Explicit common-quote calendar: endpoint differences retain the cumulative
    # move across an omitted quote date. Do not describe these as exchange daily
    # settlements or delete P&L observations after computing returns.
    panel = panel[panel.date.isin(common_dates)]
    results = {}
    for root in ["CL", "RB", "HO"]:
        contracts = [f"{root}{suffix}.NYM" for suffix in ["X26", "Z26", "F27", "G27"]]
        p = panel[
            (panel.root == root)
            & panel.contract.isin(contracts)
            & (panel.date >= "2025-01-01")
            & (panel.date < "2026-01-01")
        ]
        dates = sorted(p.date.unique())
        schedule = pd.DataFrame(
            [
                dict(date=d, contract=contracts[(pd.Timestamp(d).month - 1) // 3])
                for d in dates
            ]
        )
        # Fail on any absent selected/outgoing close instead of filling it.
        result = build_continuous(p[["date", "contract", "settlement"]], schedule)
        if len(result) < 240:
            raise ValueError("Insufficient coverage for real-data demonstration")
        result.to_csv(out / f"{root}_reconciliation.csv")
        results[root] = result
    pnl = {}
    for field in ["raw_change", "adjusted_change"]:
        legs = pd.concat(
            [
                results[root][field] * quantity
                for root, quantity in [("CL", 30000), ("RB", -840000), ("HO", -420000)]
            ],
            axis=1,
        )
        if legs.iloc[1:].isna().any().any():
            raise ValueError("Contract calendars differ; cannot silently drop P&L")
        pnl[field] = legs.sum(axis=1, min_count=3)
    pnl = pd.DataFrame(pnl).iloc[1:]
    pnl["roll_gap_pnl"] = pnl.raw_change - pnl.adjusted_change
    pnl.to_csv(out / "matched_book_pnl.csv")
    comparison = []
    forecasts = []
    for field in ["raw_change", "adjusted_change"]:
        series = pnl[field]
        var = -series.shift(1).rolling(60).quantile(0.01)
        valid = var.notna()
        comparison.append(
            dict(
                series=field,
                days=len(series),
                pnl_std=series.std(),
                historical_var_99=-series.quantile(0.01),
                worst_loss=-series.min(),
                rolling_window=60,
                forecasts=int(valid.sum()),
                exceptions=int((series[valid] < -var[valid]).sum()),
            )
        )
        forecasts.append(
            pd.DataFrame({"series": field, "pnl": series[valid], "var99": var[valid]})
        )
    pd.DataFrame(comparison).to_csv(out / "comparison.csv", index=False)
    pd.concat(forecasts).to_csv(out / "forecasts.csv")
    roll_dates = pnl[~np.isclose(pnl.roll_gap_pnl, 0)]
    roll_dates.to_csv(out / "roll_dates.csv")
    (out / "metadata.json").write_text(
        json.dumps(
            dict(
                data_type="Observed Yahoo daily Close proxies, not verified exchange settlements",
                schedule="2025 Q1: Nov2026; Q2: Dec2026; Q3: Jan2027; Q4: Feb2027, all three roots",
                purpose="Real-panel reconciliation example using available long-dated contracts; NOT the original front-month book",
                observations=len(pnl),
                roll_dates=len(roll_dates),
                incomplete_quote_dates=[str(d.date()) for d in wide.index[missing]],
                calendar="Common dates across all twelve quoted contracts; incomplete dates explicitly audited. P&L spans each remaining observation interval.",
                limitation="Arbitrary quarterly demonstration schedule, short 60-day VaR window, no validation of Yahoo roll dates or seasonal front-month jumps",
            ),
            indent=2,
        )
        + "\n"
    )
    print(pd.DataFrame(comparison).to_string(index=False))


if __name__ == "__main__":
    main()
