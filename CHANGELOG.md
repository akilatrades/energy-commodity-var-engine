# Changelog

## 1.0.0

Stable v1 release. The planned core scope is complete and active feature development is paused.

### Finalized

- multi-method VaR and Expected Shortfall framework
- component risk attribution, stress testing, backtesting, calibration sensitivity, and limit monitoring
- end-to-end demo validation and automated test coverage
- public documentation for model scope, assumptions, and limitations
- version metadata aligned to the stable v1 release
- future work reserved for maintenance, data refreshes, or clearly scoped extensions

## 0.2.0

Model-validation and repository-structure release.

### Changed

- moved portfolio, model, stress, and limit assumptions into configuration files
- replaced portfolio-level normal Monte Carlo with correlated Student-t risk-factor simulation
- added model-comparison backtesting across Historical, Parametric, and Weighted Historical VaR
- added calibration sensitivity across lookback windows and decay assumptions
- added historical replay stress scenarios derived directly from observed market moves
- tightened executive reporting and model-governance language
- renamed analytical notebooks around a focused review workflow
- consolidated supporting explanations into the core methodology and documentation
- moved synthetic/demo material out of the primary results layer
- updated CI to run both unit tests and an end-to-end demo smoke test

## 0.1.0

Initial market-risk framework with multi-commodity futures P&L, VaR, Expected Shortfall, risk attribution, stress testing, rolling validation, and illustrative limit monitoring.
