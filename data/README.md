# Market Data

The project supports two data modes.

## Historical public proxy mode

The live analysis requests daily public continuous futures proxies from Yahoo Finance for WTI crude oil, RBOB gasoline, heating oil, and Henry Hub natural gas.

The series are aligned on common dates and validated for missing values, duplicate timestamps, non-positive prices, and minimum sample length before risk calculations are run.

These public continuous futures series are research proxies. They are not a substitute for contract-specific exchange settlements or production market-data systems. Continuous-series roll construction can affect observed price changes and therefore can affect P&L and VaR estimates.

## Demo mode

Demo mode generates deterministic synthetic correlated energy prices so the full code path can run offline and in CI.

Synthetic output is for reproducibility only and is not treated as a historical market finding.
