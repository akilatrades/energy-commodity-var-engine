# Data Dictionary

## Position configuration

| Field | Definition |
|---|---|
| symbol | Public market-data symbol |
| name | Instrument description |
| contracts | Signed contract count; positive long, negative short |
| contract_multiplier | Physical units per futures contract |
| currency | Position currency |

## VaR method comparison

| Field | Definition |
|---|---|
| method | Risk methodology |
| confidence | Confidence level |
| var | Positive one-day loss threshold |
| expected_shortfall | Average modeled loss beyond the VaR threshold |

## Component VaR

| Field | Definition |
|---|---|
| symbol | Position identifier |
| marginal_var | Change in Parametric VaR per unit exposure under the linear covariance model |
| component_var | Allocated VaR contribution |
| pct_of_total_var | Contribution as a share of total Parametric VaR |
| diversifier | True when contribution is negative |

## Stress results

Hypothetical scenarios report configured percentage shocks and position P&L. Historical replay reports observed absolute price changes and corresponding fixed-book P&L.

| Field | Definition |
|---|---|
| scenario | Scenario name |
| source_type | hypothetical or historical_replay |
| source_date | Historical observation date where applicable |
| symbol_shock_pct | Configured percentage shock for hypothetical scenarios |
| symbol_price_change | Observed absolute price change for historical replay |
| symbol_pnl | Position P&L under the scenario |
| portfolio_stress_pnl | Total scenario P&L |

## Backtest summary

| Field | Definition |
|---|---|
| method | VaR model under review |
| window | Estimation-window length |
| decay | Exponential decay for Weighted Historical VaR |
| exceptions | Number of realized losses beyond forecast VaR |
| actual_exception_rate | Realized exception frequency |
| kupiec_p_value | Unconditional-coverage test p-value |
| independence_p_value | Christoffersen exception-independence p-value |
| conditional_coverage_p_value | Combined coverage and independence p-value |

## Limit monitoring

| Field | Definition |
|---|---|
| value | Current risk measure |
| limit | Configured limit |
| utilization | value divided by limit |
| status | OK, WATCH, or BREACH |
