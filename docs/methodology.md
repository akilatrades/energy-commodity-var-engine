# Methodology

## Business interpretation

The project simulates a simplified daily Market Risk process for a linear energy futures portfolio.

The workflow is:

```text
Understand positions
    -> calculate daily P&L history
    -> measure VaR / ES
    -> identify risk drivers
    -> run stress scenarios
    -> backtest VaR
    -> compare risk with a limit
    -> summarize findings for management
```

## P&L calculation

For a fixed futures position:

```text
Daily P&L
= contracts × contract multiplier × daily price change
```

A long position has positive contracts. A short position has negative contracts.

The current framework therefore models linear price risk rather than nonlinear option risk.

## Risk horizon and confidence

The main reporting convention is:

```text
1-day horizon
99% confidence
```

A 99% VaR is not a worst-case-loss estimate. It is a percentile threshold under the chosen method and data assumptions.

## Risk models

The repository compares:

- Historical VaR / Expected Shortfall
- Parametric normal VaR / Expected Shortfall
- Monte Carlo normal VaR / Expected Shortfall
- exponentially weighted historical VaR

See `var_models.md`.

## Attribution

The project decomposes normal-theory portfolio VaR into component contributions using the covariance of each position's P&L with total portfolio P&L.

See `attribution.md`.

## Validation

Rolling forecasts use only the data available before each test observation. Exceptions are then evaluated with coverage and independence diagnostics.

See `backtesting.md`.

## Control layer

An illustrative VaR limit is included to show that Market Risk is not only about calculating numbers. A risk measure also needs to be compared with approved limits and escalated when necessary.
