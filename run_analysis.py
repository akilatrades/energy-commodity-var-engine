"""Run the full energy commodity VaR project and refresh saved outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.attribution import component_var
from src.backtesting import rolling_var_forecasts, summarize_backtest
from src.data import download_yahoo_prices, make_demo_prices, save_price_snapshot
from src.limits import limit_status
from src.portfolio import default_energy_book, pnl_history_from_prices, positions_to_frame
from src.reporting import write_executive_summary
from src.stress import run_stress_scenarios
from src.var_models import summarize_var_methods

OUTPUT = Path("outputs")
DATA = Path("data")


def make_charts(pnl: pd.DataFrame, rolling: pd.DataFrame, component: pd.DataFrame) -> None:
    OUTPUT.mkdir(exist_ok=True)

    plt.figure(figsize=(11, 6))
    plt.plot(pnl.index, pnl["portfolio_pnl"] / 1_000)
    plt.axhline(0, linewidth=1)
    plt.title("Daily Portfolio P&L")
    plt.ylabel("P&L ($000)")
    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(OUTPUT / "portfolio_pnl_history.svg")
    plt.close()

    plt.figure(figsize=(11, 6))
    plt.plot(rolling.index, rolling["realized_pnl"] / 1_000, label="Realized P&L")
    plt.plot(rolling.index, -rolling["var"] / 1_000, label="99% VaR threshold")
    ex = rolling[rolling["exception"]]
    if not ex.empty:
        plt.scatter(ex.index, ex["realized_pnl"] / 1_000, label="Exceptions", s=16)
    plt.title("Rolling Historical VaR Backtest")
    plt.ylabel("$000")
    plt.xlabel("Date")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT / "var_backtest.svg")
    plt.close()

    plt.figure(figsize=(9, 6))
    plt.bar(component["symbol"], component["component_var"] / 1_000)
    plt.axhline(0, linewidth=1)
    plt.title("Parametric Component VaR")
    plt.ylabel("Component VaR ($000)")
    plt.xlabel("Position")
    plt.tight_layout()
    plt.savefig(OUTPUT / "component_var.svg")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    args = parser.parse_args()

    OUTPUT.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)

    if args.mode == "live":
        prices = download_yahoo_prices()
        save_price_snapshot(prices, DATA / "latest_public_price_snapshot.csv")
    else:
        prices = make_demo_prices()
        save_price_snapshot(prices, DATA / "demo_synthetic_prices.csv")

    positions = default_energy_book()
    positions_df = positions_to_frame(positions)
    positions_df.to_csv(OUTPUT / "portfolio_positions.csv", index=False)

    pnl = pnl_history_from_prices(prices, positions)
    pnl.index.name = "date"
    pnl.to_csv(OUTPUT / "daily_position_pnl.csv")

    var_summary = summarize_var_methods(pnl["portfolio_pnl"], confidence=0.99)
    var_summary.to_csv(OUTPUT / "var_method_comparison.csv", index=False)

    component = component_var(pnl, confidence=0.99)
    component.to_csv(OUTPUT / "component_var.csv", index=False)

    stresses = run_stress_scenarios(prices.iloc[-1], positions)
    stresses.to_csv(OUTPUT / "stress_scenarios.csv", index=False)

    rolling = rolling_var_forecasts(
        pnl["portfolio_pnl"], window=250, confidence=0.99, method="historical"
    )
    rolling.to_csv(OUTPUT / "historical_var_backtest.csv")
    backtest_summary = summarize_backtest(rolling, confidence=0.99)
    backtest_summary.to_csv(OUTPUT / "backtest_summary.csv", index=False)

    hist_var = float(var_summary.loc[var_summary["method"] == "Historical", "var"].iloc[0])
    risk_limit = limit_status(hist_var, limit=500_000)
    pd.DataFrame([risk_limit]).to_csv(OUTPUT / "limit_monitoring.csv", index=False)

    make_charts(pnl, rolling, component)

    write_executive_summary(
        OUTPUT / "executive_summary.md",
        data_mode=args.mode,
        var_summary=var_summary,
        component=component,
        stresses=stresses,
        backtest_summary=backtest_summary,
        limit_status=risk_limit,
    )

    print(f"Analysis complete in {args.mode.upper()} mode. See outputs/.")


if __name__ == "__main__":
    main()
