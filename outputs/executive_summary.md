# Executive Market Risk Summary

## Scope

Illustrative energy futures portfolio risk review using WTI crude, RBOB gasoline, heating oil, and Henry Hub natural gas.

**DEMO / SYNTHETIC DATA** — results demonstrate the workflow only.

## Daily VaR and Expected Shortfall

- 99% Historical VaR: **$737,315**
- 99% Historical Expected Shortfall: **$983,001**
- 99% Parametric VaR: **$581,745**
- 99% Monte Carlo VaR: **$584,330**

## Main risk driver

Largest parametric component VaR contribution: **NG=F**, approximately **$503,544**.

A negative component contribution would indicate diversification rather than risk concentration.

## Stress testing

Worst predefined scenario: **Refined-products squeeze**, modeled portfolio P&L **$-1,154,999**.

## Backtesting

- Test observations: **1249**
- VaR exceptions: **20**
- Actual exception rate: **1.60%**
- Kupiec coverage p-value: **0.050**
- Independence test pass at 5%: **True**

Backtesting is a model diagnostic, not proof that future losses are bounded by VaR.

## Limit monitoring

Illustrative VaR limit utilization: **147.5%** — **BREACH**.

## Model-use note

This project is an analytical portfolio project rather than a production market-risk platform. A bank or trading firm would additionally require independent market data, instrument-level pricing and sensitivities, intraday controls, governance, model validation, limit approvals, P&L explain, and auditable production systems.
