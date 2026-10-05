# Data Dictionary

## Portfolio positions

| Field | Meaning |
|---|---|
| `symbol` | Market-data symbol used by the project. |
| `name` | Human-readable market name. |
| `contracts` | Signed number of futures contracts; positive = long, negative = short. |
| `contract_multiplier` | Physical units represented by one contract. |
| `currency` | Position currency. |

## Daily P&L

| Field | Meaning |
|---|---|
| instrument symbol | Daily P&L of that fixed futures position. |
| `portfolio_pnl` | Sum of all position P&L columns. |

## VaR summary

| Field | Meaning |
|---|---|
| `method` | Risk-model name. |
| `confidence` | VaR confidence level. |
| `var` | Positive loss magnitude at the VaR threshold. |
| `expected_shortfall` | Average loss beyond VaR, where implemented. |

## Component VaR

| Field | Meaning |
|---|---|
| `marginal_var` | Change in total VaR per unit exposure under the simplified normal framework. |
| `component_var` | Allocated VaR contribution from the position. |
| `pct_of_total_var` | Component contribution divided by total parametric VaR. |
| `diversifier` | True when component contribution is negative. |

## Backtesting

| Field | Meaning |
|---|---|
| `realized_pnl` | Next observed portfolio P&L. |
| `var` | VaR estimated using prior observations. |
| `exception` | True when realized loss exceeds VaR. |
| `actual_exception_rate` | Exceptions divided by test observations. |
| `lr_pof` | Kupiec likelihood-ratio statistic. |
| `kupiec_p_value` | Kupiec test p-value. |
| `lr_independence` | Christoffersen independence likelihood-ratio statistic. |
| `independence_p_value` | Christoffersen independence test p-value. |

## Limit monitoring

| Field | Meaning |
|---|---|
| `value` | Current risk measure. |
| `limit` | Illustrative approved limit. |
| `utilization` | value / limit. |
| `status` | `OK`, `WATCH`, or `BREACH`. |
