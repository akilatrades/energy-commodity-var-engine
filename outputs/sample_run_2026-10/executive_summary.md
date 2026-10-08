# Executive Market Risk Summary

**As of:** 2026-10-07
**Data basis:** Public continuous futures proxies; not production exchange settlement data.

## Portfolio risk

| Method | 99% 1-day VaR | 99% Expected Shortfall |
|---|---:|---:|
| Historical | $181,399 | $195,300 |
| Parametric Normal | $161,159 | $184,634 |
| Monte Carlo Student-t (df=6) | $175,837 | $222,113 |
| Weighted Historical (lambda=0.97) | $128,292 | $162,354 |

Largest component VaR contributor: **RB=F** at approximately **$101,872**.

## Stress testing

Worst configured hypothetical scenario: **Product rally hedge loss physical margin gain**, portfolio P&L **$-931,652**.

Worst observed historical replay in the analyzed sample: **Historical replay 2020-04-20**, portfolio P&L **$-1,612,614**.

## Model validation

| Method | Exceptions | Actual rate | Kupiec p | Independence p | Conditional coverage p |
|---|---:|---:|---:|---:|---:|
| historical | 42 | 2.15% | 0.000 | 0.000 | 0.000 |
| parametric | 44 | 2.25% | 0.000 | 0.000 | 0.000 |
| weighted_historical | 44 | 2.25% | 0.000 | 0.018 | 0.000 |

Validation results are diagnostics. They do not establish that future losses are bounded by VaR and should be reviewed alongside stress results, parameter sensitivity, market conditions, and data quality.

## Limit monitoring

Current Historical VaR: **$181,399**
Approved illustrative limit: **$500,000**
Utilization: **36.3%**
Status: **OK**

## Model-use boundary

This repository is an analytical Market Risk portfolio project. Production use would require contract-level market data, independent price verification, full instrument pricing and sensitivities, intraday controls, liquidity and concentration treatment, P&L explain, formal model governance, and auditable trading-system integration.
