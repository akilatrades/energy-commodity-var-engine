"""Management-style report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_executive_summary(
    path: str | Path,
    data_mode: str,
    var_summary: pd.DataFrame,
    component: pd.DataFrame,
    stresses: pd.DataFrame,
    backtest_summary: pd.DataFrame,
    limit_status: dict,
) -> None:
    """Write a concise market-risk executive summary."""
    hist = var_summary[var_summary["method"] == "Historical"].iloc[0]
    para = var_summary[var_summary["method"] == "Parametric Normal"].iloc[0]
    mc = var_summary[var_summary["method"] == "Monte Carlo Normal"].iloc[0]
    top = component.iloc[0]
    worst = stresses.sort_values("portfolio_stress_pnl").iloc[0]
    bt = backtest_summary.iloc[0]

    mode_note = (
        "**DEMO / SYNTHETIC DATA** — results demonstrate the workflow only."
        if data_mode.lower() == "demo"
        else "Public continuous futures proxy data; see data and model limitations."
    )

    text = f"""# Executive Market Risk Summary

## Scope

Illustrative energy futures portfolio risk review using WTI crude, RBOB gasoline, heating oil, and Henry Hub natural gas.

{mode_note}

## Daily VaR and Expected Shortfall

- 99% Historical VaR: **${hist['var']:,.0f}**
- 99% Historical Expected Shortfall: **${hist['expected_shortfall']:,.0f}**
- 99% Parametric VaR: **${para['var']:,.0f}**
- 99% Monte Carlo VaR: **${mc['var']:,.0f}**

## Main risk driver

Largest parametric component VaR contribution: **{top['symbol']}**, approximately **${top['component_var']:,.0f}**.

A negative component contribution would indicate diversification rather than risk concentration.

## Stress testing

Worst predefined scenario: **{worst['scenario']}**, modeled portfolio P&L **${worst['portfolio_stress_pnl']:,.0f}**.

## Backtesting

- Test observations: **{int(bt['observations'])}**
- VaR exceptions: **{int(bt['exceptions'])}**
- Actual exception rate: **{bt['actual_exception_rate']:.2%}**
- Kupiec coverage p-value: **{bt['kupiec_p_value']:.3f}**
- Independence test pass at 5%: **{bool(bt['independence_pass_5pct'])}**

Backtesting is a model diagnostic, not proof that future losses are bounded by VaR.

## Limit monitoring

Illustrative VaR limit utilization: **{limit_status['utilization']:.1%}** — **{limit_status['status']}**.

## Model-use note

This project is an analytical portfolio project rather than a production market-risk platform. A bank or trading firm would additionally require independent market data, instrument-level pricing and sensitivities, intraday controls, governance, model validation, limit approvals, P&L explain, and auditable production systems.
"""
    Path(path).write_text(text)
