"""Management-style market-risk reporting."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _money(value: float) -> str:
    return f"${value:,.0f}"


def write_executive_summary(
    path: str | Path,
    as_of: str,
    data_mode: str,
    var_summary: pd.DataFrame,
    component: pd.DataFrame,
    hypothetical_stress: pd.DataFrame,
    historical_stress: pd.DataFrame,
    backtest_summary: pd.DataFrame,
    limit_result: dict,
) -> None:
    """Write a concise risk summary focused on decision-relevant results."""
    top = component.iloc[0]
    worst_hypo = hypothetical_stress.nsmallest(1, "portfolio_stress_pnl").iloc[0]
    worst_hist = historical_stress.nsmallest(1, "portfolio_stress_pnl").iloc[0]

    risk_rows = "\n".join(
        f"| {row.method} | {_money(row.var)} | {_money(row.expected_shortfall)} |"
        for row in var_summary.itertuples(index=False)
    )

    validation_rows = "\n".join(
        f"| {row.method} | {int(row.exceptions)} | {row.actual_exception_rate:.2%} | "
        f"{row.kupiec_p_value:.3f} | {row.independence_p_value:.3f} | "
        f"{row.conditional_coverage_p_value:.3f} |"
        for row in backtest_summary.itertuples(index=False)
    )

    data_note = (
        "DEMO / SYNTHETIC DATA — workflow validation only."
        if data_mode == "demo"
        else "Public continuous futures proxies; not production exchange settlement data."
    )

    text = f"""# Executive Market Risk Summary

**As of:** {as_of}
**Data basis:** {data_note}

## Portfolio risk

| Method | 99% 1-day VaR | 99% Expected Shortfall |
|---|---:|---:|
{risk_rows}

Largest component VaR contributor: **{top["symbol"]}** at approximately **{_money(float(top["component_var"]))}**.

## Stress testing

Worst configured hypothetical scenario: **{worst_hypo["scenario"]}**, portfolio P&L **{_money(float(worst_hypo["portfolio_stress_pnl"]))}**.

Worst observed historical replay in the analyzed sample: **{worst_hist["scenario"]}**, portfolio P&L **{_money(float(worst_hist["portfolio_stress_pnl"]))}**.

## Model validation

| Method | Exceptions | Actual rate | Kupiec p | Independence p | Conditional coverage p |
|---|---:|---:|---:|---:|---:|
{validation_rows}

Validation results are diagnostics. They do not establish that future losses are bounded by VaR and should be reviewed alongside stress results, parameter sensitivity, market conditions, and data quality.

## Limit monitoring

Current Historical VaR: **{_money(float(limit_result["value"]))}**
Approved illustrative limit: **{_money(float(limit_result["limit"]))}**
Utilization: **{limit_result["utilization"]:.1%}**
Status: **{limit_result["status"]}**

## Model-use boundary

This repository is an analytical Market Risk portfolio project. Production use would require contract-level market data, independent price verification, full instrument pricing and sensitivities, intraday controls, liquidity and concentration treatment, P&L explain, formal model governance, and auditable trading-system integration.
"""
    Path(path).write_text(text, encoding="utf-8")
