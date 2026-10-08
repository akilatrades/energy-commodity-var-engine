"""Diagnose the fixed October sample without deleting or relabeling losses."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import fisher_exact

from src.backtesting import rolling_var_forecasts, summarize_backtest
from src.filtered_historical import filtered_forecasts, month_turn_flags
from src.portfolio import load_positions_csv, pnl_history_from_prices


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prices", default="outputs/sample_run_2026-10/input_prices.csv"
    )
    parser.add_argument("--output-dir", default="outputs/diagnosis_2026-10")
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    prices = pd.read_csv(args.prices, index_col="date", parse_dates=True)
    positions = load_positions_csv("config/portfolio.csv")
    contributions = pnl_history_from_prices(prices, positions)
    pnl = contributions.portfolio_pnl
    original = rolling_var_forecasts(pnl)
    bands = []
    for first, last in [(2, 2), (3, 2), (2, 3), (3, 3)]:
        flag = month_turn_flags(original.index, first, last)
        exceptions = original.exception
        a = int((flag & exceptions).sum())
        b = int((flag & ~exceptions).sum())
        c = int((~flag & exceptions).sum())
        d = int((~flag & ~exceptions).sum())
        odds, pvalue = fisher_exact([[a, b], [c, d]])
        bands.append(
            dict(
                first_weekdays=first,
                last_weekdays=last,
                flagged_dates=int(flag.sum()),
                dates=len(flag),
                flagged_exception_count=a,
                exceptions=int(exceptions.sum()),
                calendar_baseline=float(flag.mean()),
                exception_share_flagged=float(flag[exceptions].mean()),
                odds_ratio=odds,
                descriptive_fisher_p=pvalue,
            )
        )
    pd.DataFrame(bands).to_csv(output / "calendar_diagnostic.csv", index=False)
    original.groupby(original.index.year).exception.agg(["sum", "count"]).rename(
        columns={"sum": "exceptions", "count": "forecasts"}
    ).to_csv(output / "baseline_exceptions_by_year.csv")
    original.join(contributions.drop(columns="portfolio_pnl")).nsmallest(
        30, "realized_pnl"
    ).to_csv(output / "largest_losses_by_leg.csv")
    rb = prices["RB=F"].diff().dropna()
    pd.DataFrame(
        {
            "RB_change_usd_per_gal": rb,
            "RB_hedge_pnl_usd": rb * -840000,
            "calendar_flag": month_turn_flags(rb.index),
        }
    ).loc[rb.abs().nlargest(30).index].to_csv(output / "largest_rb_changes.csv")

    flags = month_turn_flags(pnl.index)
    # Predeclared fixed decays: primary .94, sensitivities .97 and .99.
    # No parameter is selected by which one passes a test.
    forecasts = []
    raw = filtered_forecasts(pnl, filtered=False)
    forecasts.append(raw)
    raw_excluded = filtered_forecasts(pnl, filtered=False, exclude_training_flags=flags)
    forecasts.append(raw_excluded)
    for decay in [0.94, 0.97, 0.99]:
        fhs = filtered_forecasts(pnl, decay=decay)
        fhs["method"] = f"ewma_fhs_{decay}"
        forecasts.append(fhs)
    combined = filtered_forecasts(pnl, exclude_training_flags=flags)
    forecasts.append(combined)
    for method in ["parametric", "weighted_historical"]:
        base = rolling_var_forecasts(pnl, method=method, decay=0.97)
        forecasts.append(base.loc[raw.index])
    all_forecasts = pd.concat(forecasts)
    all_forecasts.reset_index().to_csv(
        output / "forecasts.csv.gz",
        index=False,
        compression={"method": "gzip", "mtime": 0},
    )
    all_forecasts[all_forecasts.exception].reset_index().to_csv(
        output / "exception_ledger.csv", index=False
    )
    summaries = []
    for f in forecasts:
        for period in ["all_common_dates", "before_2024", "2024_onward"]:
            segment = f
            if period == "before_2024":
                segment = f[f.index < "2024-01-01"]
            elif period == "2024_onward":
                segment = f[f.index >= "2024-01-01"]
            row = summarize_backtest(segment)
            row["period"] = period
            row["average_var"] = segment["var"].mean()
            row["start"] = str(segment.index[0].date())
            row["end"] = str(segment.index[-1].date())
            summaries.append(row)
    summary = pd.concat(summaries, ignore_index=True)
    summary.to_csv(output / "model_comparison.csv", index=False)
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for name, ax in zip(["historical_common", "ewma_fhs_0.94"], axes):
        f = all_forecasts[all_forecasts.method == name]
        ax.plot(
            f.index,
            -f.realized_pnl / 1000,
            color="gray",
            alpha=0.5,
            label="Realized loss",
        )
        ax.plot(f.index, f["var"] / 1000, label="99% VaR")
        e = f[f.exception]
        ax.scatter(
            e.index, -e.realized_pnl / 1000, s=15, color="red", label="Exception"
        )
        ax.set(title=name.replace("_", " "), ylabel="USD thousands")
        ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(output / "backtest_comparison.svg")
    plt.close(fig)
    metadata = dict(
        input_sha256=hashlib.sha256(Path(args.prices).read_bytes()).hexdigest(),
        confidence=0.99,
        window=250,
        warmup=60,
        primary_decay=0.94,
        sensitivity_decays=[0.97, 0.99],
        calendar_first_weekdays=3,
        calendar_last_weekdays=2,
        calendar_holidays="not adjusted",
        excluded_realized_losses=0,
        actual_roll_corrections=0,
        interpretation="retrospective diagnostics; 2024 onward is a stability segment, not an untouched holdout",
    )
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(
        summary[summary.period == "all_common_dates"][
            [
                "method",
                "observations",
                "exceptions",
                "actual_exception_rate",
                "kupiec_p_value",
                "independence_p_value",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
