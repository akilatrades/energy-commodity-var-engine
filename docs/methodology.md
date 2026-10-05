# Methodology

## Objective

The framework measures and validates daily market risk for a fixed linear energy futures portfolio.

The process is deliberately separated into distinct control questions:

1. What positions are in the book?
2. What daily P&L would those positions have produced?
3. What do alternative VaR and Expected Shortfall methods report?
4. Which positions contribute most to risk?
5. How does the portfolio behave under severe market moves?
6. Do VaR forecasts perform reasonably out of sample?
7. How sensitive are validation results to key calibration choices?
8. Is current risk within the configured limit?

## Portfolio P&L

For a fixed linear futures position:

Daily P&L = contracts × contract multiplier × daily price change.

Position P&L is calculated independently by market and then aggregated to portfolio P&L.

The project uses direct settlement-price changes and contract multipliers for historical futures P&L.

## Current risk window

Current VaR, Expected Shortfall, Monte Carlo calibration, and component VaR use the most recent configurable risk window, set to 250 daily P&L observations by default.

The longer history is retained for rolling validation, calibration sensitivity, and historical stress replay.

This separation avoids using the entire available history as the current volatility estimate while still preserving a broader sample for model review.

## Risk horizon

The primary convention is 99% one-day VaR and Expected Shortfall.

A VaR estimate is a model percentile, not a maximum possible loss.

## Model comparison

The project reports Historical, Parametric Normal, correlated Student-t Monte Carlo, and Weighted Historical estimates side by side.

No single method is treated as automatically superior. Method selection should be supported by assumptions, observed behavior, validation, stress testing, and the intended use of the metric.

## Validation

Historical, Parametric, and Weighted Historical VaR are evaluated using rolling out-of-sample forecasts. The project reports unconditional coverage, exception independence, combined conditional coverage, and parameter sensitivity.

See **model_validation.md**.

## Control layer

Current Historical VaR is compared with a configurable illustrative limit. Limit status is separate from model validation: a model can pass validation while the portfolio breaches a limit, and a portfolio can be within limit while the model itself requires review.
