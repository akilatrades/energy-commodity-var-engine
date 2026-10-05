# Changelog

## 0.2.0

Professionalization and model-validation release.

### Changed

- moved portfolio, model, stress, and limit assumptions into configuration files
- replaced portfolio-level normal Monte Carlo with correlated Student-t risk-factor simulation
- added model-comparison backtesting across Historical, Parametric, and Weighted Historical VaR
- added calibration sensitivity across lookback windows and decay assumptions
- added historical replay stress scenarios derived directly from observed market moves
- tightened executive reporting and model-governance language
- renamed analytical notebooks around professional review workflow
- removed beginner-facing documentation from the public repository
- moved synthetic/demo material out of the primary results layer
- updated CI to run both unit tests and an end-to-end demo smoke test

## 0.1.0

Initial market-risk framework with multi-commodity futures P&L, VaR, Expected Shortfall, risk attribution, stress testing, rolling validation, and illustrative limit monitoring.
