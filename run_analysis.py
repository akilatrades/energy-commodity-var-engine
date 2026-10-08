"""Run the energy commodity market-risk analysis."""

from __future__ import annotations

import argparse
import json
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.attribution import component_var
from src.backtesting import calibration_sensitivity, compare_backtests
from src.data import download_yahoo_prices, make_demo_prices, save_price_snapshot, validate_price_history
from src.limits import limit_status, load_risk_limits
from src.portfolio import load_positions_csv, pnl_history_from_prices, positions_to_frame
from src.reporting import write_executive_summary
from src.stress import (
    historical_replay_scenarios,
    load_stress_scenarios,
    run_hypothetical_scenarios,
)
from src.var_models import summarize_var_methods


CONFIG = Path("config")
DATA = Path("data")


def load_model_config() -> dict:
    with open(CONFIG / "model_config.json", "r", encoding="utf-8") as handle:
        return json.load(handle)


def make_charts(
    output: Path,
    pnl: pd.DataFrame,
    forecasts: pd.DataFrame,
    component: pd.DataFrame,
) -> None:
    output.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(11, 6))
    plt.plot(pnl.index, pnl["portfolio_pnl"] / 1_000)
    plt.axhline(0, linewidth=1)
    plt.title("Daily Portfolio P&L")
    plt.ylabel("P&L ($000)")
    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(output / "portfolio_pnl_history.svg")
    plt.close()

    historical = forecasts[forecasts["method"] == "historical"].copy()
    historical["date"] = pd.to_datetime(historical["date"])
    plt.figure(figsize=(11, 6))
    plt.plot(
        historical["date"],
        historical["realized_pnl"] / 1_000,
        label="Realized P&L",
    )
    plt.plot(
        historical["date"],
        -historical["var"] / 1_000,
        label="99% VaR threshold",
    )
    exceptions = historical[historical["exception"]]
    if not exceptions.empty:
        plt.scatter(
            exceptions["date"],
            exceptions["realized_pnl"] / 1_000,
            label="Exceptions",
            s=16,
        )
    plt.title("Rolling Historical VaR Backtest")
    plt.ylabel("$000")
    plt.xlabel("Date")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "var_backtest.svg")
    plt.close()

    plt.figure(figsize=(9, 6))
    plt.bar(component["symbol"], component["component_var"] / 1_000)
    plt.axhline(0, linewidth=1)
    plt.title("Parametric Component VaR")
    plt.ylabel("Component VaR ($000)")
    plt.xlabel("Position")
    plt.tight_layout()
    plt.savefig(output / "component_var.svg")
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "live", "snapshot"], required=True)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--prices", help="Previously saved public prices CSV for snapshot mode")
    parser.add_argument("--end", help="Exclusive live download end date (YYYY-MM-DD)")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    model = load_model_config()
    positions = load_positions_csv(CONFIG / "portfolio.csv")
    stress_config = load_stress_scenarios(CONFIG / "stress_scenarios.csv")
    limits = load_risk_limits(CONFIG / "risk_limits.json")

    if args.mode == "live":
        prices = download_yahoo_prices(
            [p.symbol for p in positions],
            start=model["historical_start"],
            end=args.end,
        )
        save_price_snapshot(prices, DATA / "latest_public_price_snapshot.csv")
    elif args.mode == "snapshot":
        if not args.prices:
            parser.error("--prices is required for snapshot mode")
        prices = pd.read_csv(args.prices, index_col="date", parse_dates=True)
        validate_price_history(prices)
    else:
        prices = make_demo_prices()
        save_price_snapshot(prices, DATA / "demo_synthetic_prices.csv")

    # Store exact input prices/configs alongside each point-in-time result.
    save_price_snapshot(prices, output / "input_prices.csv")
    for config_path in CONFIG.glob("*"):
        if config_path.is_file():
            (output / "config").mkdir(exist_ok=True)
            shutil.copyfile(config_path, output / "config" / config_path.name)

    pnl = pnl_history_from_prices(prices, positions)

    positions_to_frame(positions).to_csv(
        output / "portfolio_positions.csv", index=False
    )
    pnl.index.name = "date"
    pnl.to_csv(output / "daily_position_pnl.csv")

    risk_window = int(model["current_risk_window"])
    if len(pnl) < risk_window:
        raise ValueError(
            f"Current risk window requires {risk_window} P&L observations; got {len(pnl)}."
        )
    current_pnl = pnl.iloc[-risk_window:]
    current_prices = prices.iloc[-(risk_window + 1):]

    var_summary = summarize_var_methods(
        current_pnl["portfolio_pnl"],
        prices=current_prices,
        positions=positions,
        confidence=model["confidence"],
        decay=model["weighted_decay"],
        n_sims=model["monte_carlo_sims"],
        monte_carlo_df=model["monte_carlo_student_t_df"],
        mean_adjusted=model["parametric_mean_adjusted"],
    )
    var_summary.to_csv(output / "var_method_comparison.csv", index=False)

    component = component_var(current_pnl, confidence=model["confidence"])
    component.to_csv(output / "component_var.csv", index=False)

    hypothetical = run_hypothetical_scenarios(
        prices.iloc[-1],
        positions,
        stress_config,
    )
    hypothetical.to_csv(output / "hypothetical_stress_scenarios.csv", index=False)

    historical = historical_replay_scenarios(
        prices,
        positions,
        count=model["historical_stress_count"],
    )
    historical.to_csv(output / "historical_replay_stress.csv", index=False)

    backtest_summary, forecasts = compare_backtests(
        pnl["portfolio_pnl"],
        methods=model["backtest_methods"],
        window=model["backtest_window"],
        confidence=model["confidence"],
        decay=model["weighted_decay"],
        mean_adjusted=model["parametric_mean_adjusted"],
    )
    backtest_summary.to_csv(output / "var_backtest_summary.csv", index=False)
    forecasts.to_csv(output / "var_backtest_forecasts.csv", index=False)

    sensitivity = calibration_sensitivity(
        pnl["portfolio_pnl"],
        windows=model["sensitivity_windows"],
        confidence=model["confidence"],
        decays=model["sensitivity_decays"],
        mean_adjusted=model["parametric_mean_adjusted"],
    )
    sensitivity.to_csv(output / "calibration_sensitivity.csv", index=False)

    historical_var_value = float(
        var_summary.loc[var_summary["method"] == "Historical", "var"].iloc[0]
    )
    limit_result = limit_status(
        historical_var_value,
        limit=float(limits["var_99_1d_usd"]),
        watch_threshold=float(limits["watch_utilization"]),
    )
    pd.DataFrame([limit_result]).to_csv(
        output / "limit_monitoring.csv", index=False
    )

    make_charts(output, pnl, forecasts, component)

    as_of = pd.Timestamp(prices.index[-1]).date().isoformat()
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "as_of": as_of,
        "mode": args.mode,
        "data_source": (
            "Yahoo Finance public continuous futures proxies"
            if args.mode in {"live", "snapshot"}
            else "deterministic synthetic demo data"
        ),
        "observations": int(len(prices)),
        "symbols": [p.symbol for p in positions],
        "confidence": model["confidence"],
        "current_risk_window": risk_window,
        "backtest_window": model["backtest_window"],
        "input_prices_sha256": hashlib.sha256((output / "input_prices.csv").read_bytes()).hexdigest(),
        "requested_end_exclusive": args.end,
        "portfolio_thesis": "Refiner 3-2-1 margin hedge; financial hedge book only",
    }
    (output / "analysis_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    write_executive_summary(
        output / "executive_summary.md",
        as_of=as_of,
        data_mode=args.mode,
        var_summary=var_summary,
        component=component,
        hypothetical_stress=hypothetical,
        historical_stress=historical,
        backtest_summary=backtest_summary,
        limit_result=limit_result,
    )

    (output / "README.md").write_text(
        "# Point-in-time risk sample\n\n"
        + ("**SYNTHETIC DEMO. Not observed market performance.**\n\n" if args.mode == "demo" else "**Public-data historical sample; not a forecast or live risk feed.**\n\n")
        + f"Last price date: {as_of}. Generation timestamp and input checksum are in `analysis_metadata.json`.\n\n"
        + "The book is +30 CL, -20 RB and -10 HO contracts: a refiner's financial hedge of a 30,000-bbl 3-2-1 margin exposure. Physical margin is excluded. A hedge loss can offset a physical gain.\n\n"
        + "Read `executive_summary.md`, `var_method_comparison.csv`, `var_backtest_summary.csv`, and the stress tables. `var_backtest.svg` plots forecasts against subsequent P&L. Exact prices and configuration are saved here.\n\n"
        + "The Yahoo continuous proxies have unknown roll construction. The contract-panel roll builder is a separate, tested module and has not been applied to these proxy prices.\n",
        encoding="utf-8",
    )

    print(f"Analysis complete in {args.mode.upper()} mode. Results: {output}")


if __name__ == "__main__":
    main()
