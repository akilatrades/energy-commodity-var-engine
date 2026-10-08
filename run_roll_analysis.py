"""Compare raw and roll-adjusted P&L from a user-supplied contract panel."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.continuous import build_continuous
from src.var_models import historical_es, historical_var


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--settlements", required=True)
    p.add_argument("--schedule", required=True)
    p.add_argument("--output-dir", default="outputs/roll_analysis")
    p.add_argument("--contracts", type=int, default=1)
    p.add_argument("--multiplier", type=float, default=1000)
    p.add_argument(
        "--data-label",
        required=True,
        help="Source identity; mark synthetic fixtures explicitly",
    )
    a = p.parse_args()
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    series = build_continuous(pd.read_csv(a.settlements), pd.read_csv(a.schedule))
    series.to_csv(out / "continuous_series.csv")
    rows = []
    for name in ["raw", "adjusted"]:
        pnl = series[name + "_change"].dropna() * a.contracts * a.multiplier
        rows.append(
            dict(
                series=name,
                var_99=historical_var(pnl),
                es_99=historical_es(pnl),
                pnl_std=pnl.std(),
                data_label=a.data_label,
            )
        )
    pd.DataFrame(rows).to_csv(out / "roll_var_comparison.csv", index=False)
    ax = series[["raw_change", "adjusted_change"]].plot(
        figsize=(9, 4), title="Roll jumps versus held-contract price changes"
    )
    ax.set_ylabel("$/bbl per observation")
    ax.figure.tight_layout()
    ax.figure.savefig(out / "roll_effect.svg")
    plt.close(ax.figure)


if __name__ == "__main__":
    main()
