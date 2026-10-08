# Model Limitations and Use Boundary

This repository is an analytical Market Risk portfolio project, not a production risk platform.

## Instruments

The default refiner hedge book contains linear futures. A separate one-factor WTI option case study now supports European Black-76 full revaluation.

The option case study excludes volatility surfaces, American exercise, average-price settlement and path-dependent derivatives. It is not combined with the default refiner book.

## Market data

Historical mode uses public continuous futures proxies.

A production implementation would require exact instrument identifiers, official or independently validated settlement prices, contract calendars, explicit roll logic, timestamp controls, stale-price checks, and governed market-data lineage.

Continuous futures construction can introduce roll-related price changes that influence calculated P&L and VaR. The new contract-panel roll builder is tested on a synthetic fixture; it does not correct the Yahoo proxy used in the live sample. See continuous_series.md.

## VaR

Historical VaR is sample dependent and cannot represent events absent from the historical window.

Parametric Normal VaR can understate fat-tail behavior.

Student-t Monte Carlo still depends on estimated covariance, a chosen degrees-of-freedom parameter, fixed linear sensitivities, and a stationary-distribution assumption.

Weighted Historical VaR adds a decay parameter that introduces additional calibration risk.

No VaR method is a maximum-loss estimate.

## Portfolio assumptions

The analysis holds contract counts fixed across the historical P&L sample. It therefore measures the historical behavior of today's illustrative position structure rather than reconstructing an actual evolving trading book.

The project does not include intraday position changes, FX translation, transaction costs, liquidity add-ons, concentration add-ons, initial or variation margin, funding, or counterparty credit risk.

## Validation

Backtest results are sample dependent. At 99% confidence, exceptions are intentionally rare, which limits statistical power in short samples.

The project does not optimize parameters solely to improve p-values.

## Production-control gap

A production Market Risk environment would additionally require trade-capture controls, independent valuations, risk-factor mapping, sensitivity validation, P&L explain, formal limit governance, model approval, change management, access control, audit trails, business continuity, and integration with front-office and risk systems.
