"""Run from this directory. Uses the committed front-month price snapshot."""

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from model import (
    ENTRY_Z,
    NEGATIVE_WTI_DATES,
    WINDOW,
    contract_roll_days,
    crack_history,
    excluded_days,
    load_prices,
    mean_reversion_position,
    next_day_pnl,
    summarize,
    zscore,
)

SOURCE = Path("data/front_month_proxies_2018_2026.csv")


def main():
    out = Path("outputs")
    out.mkdir(exist_ok=True)
    prices = load_prices(SOURCE)
    cracks = crack_history(prices)
    cracks.to_csv(out / "crack_history.csv")

    annual = cracks.crack_321.groupby(cracks.index.year).agg(
        trading_days="count",
        mean="mean",
        p10=lambda x: x.quantile(0.10),
        p90=lambda x: x.quantile(0.90),
        low="min",
        high="max",
    )
    annual.index.name = "year"
    annual.to_csv(out / "annual_321_crack.csv")

    crack = cracks.crack_321
    exclude = excluded_days(crack.index)
    position = mean_reversion_position(zscore(crack))
    rows = [
        summarize(next_day_pnl(crack, position, exclude), "primary"),
        summarize(
            next_day_pnl(crack, position.where(crack.index.year != 2020), exclude),
            "excluding_2020",
        ),
        summarize(next_day_pnl(crack, position), "roll_days_included"),
        summarize(
            next_day_pnl(crack, position.shift(-1), exclude),
            "look_ahead_error_demo",
        ),
    ]
    results = pd.DataFrame(rows)
    results.to_csv(out / "signal_test.csv", index=False)

    roll = contract_roll_days(crack.index) & ~crack.index.isin(NEGATIVE_WTI_DATES)
    change = crack.diff().abs()
    roll_check = pd.DataFrame(
        [
            {
                "day_type": "first_trading_day_of_month",
                "mean_abs_change": change[roll].mean(),
            },
            {"day_type": "other_days", "mean_abs_change": change[~exclude].mean()},
        ]
    )
    roll_check.to_csv(out / "roll_day_check.csv", index=False)

    (out / "assumptions.json").write_text(
        json.dumps(
            {
                "input": str(SOURCE),
                "input_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                "data_class": "Yahoo Finance continuous front-month futures proxies",
                "sample_start": str(crack.index[0].date()),
                "sample_end": str(crack.index[-1].date()),
                "crack": "(2 x RB x 42 + 1 x HO x 42 - 3 x CL) / 3, USD/bbl",
                "signal": f"z-score vs trailing {WINDOW} days; short above +{ENTRY_Z}, long below -{ENTRY_Z}",
                "timing": "Position set at close t from data through t; P&L is the t to t+1 crack change",
                "excluded": "Changes into the first trading day of each month (product rolls) and April 20-22, 2020",
                "costs": "None; results are before transaction costs",
            },
            indent=2,
        )
        + "\n"
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(cracks.index, cracks.crack_321, color="#1f3a5f", lw=0.9)
    ax.set(
        ylabel="USD/bbl",
        title="NYMEX 3-2-1 crack spread from front-month proxies",
    )
    fig.tight_layout()
    fig.savefig(out / "crack_321_history.svg")
    plt.close(fig)

    print(annual.round(2).to_string())
    print(results.round(3).to_string(index=False))
    print(roll_check.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
