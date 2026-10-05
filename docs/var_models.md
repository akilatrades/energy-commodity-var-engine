# VaR and Expected Shortfall Models

## Historical

Historical VaR uses the observed portfolio P&L distribution directly. Historical Expected Shortfall measures the average loss beyond the historical VaR threshold.

Primary strengths are transparency and minimal distributional assumptions. Primary limitations are dependence on the selected sample and slow response when old observations receive the same weight as recent observations.

## Parametric Normal

Parametric VaR estimates portfolio volatility and maps the selected confidence level through the normal distribution.

The default project configuration assumes zero expected one-day P&L rather than estimating a short-horizon drift.

This method is fast and transparent, but normality can understate fat-tail behavior and regime changes.

## Correlated Student-t Monte Carlo

Monte Carlo is implemented at the market-factor level rather than by drawing directly from a fitted portfolio P&L distribution.

The model:

1. estimates the covariance matrix of daily absolute futures price changes across the four energy markets;
2. converts that covariance into a multivariate Student-t scale matrix;
3. draws correlated heavy-tailed futures price changes;
4. applies those simulated changes through each contract multiplier and signed position;
5. aggregates simulated position P&L into portfolio P&L;
6. calculates VaR and Expected Shortfall from the simulated distribution.

Absolute price changes are used because the historical P&L engine is also based on settlement-price changes and because futures prices can approach or cross zero.

The degrees of freedom and simulation count are explicit configuration assumptions.

This creates a meaningfully different tail model from Normal Parametric VaR while remaining explainable.

## Weighted Historical

Weighted Historical VaR assigns larger probability weight to recent P&L observations using exponential decay.

The decay parameter is not optimized to make a backtest pass. The project reports sensitivity across multiple decay values so the calibration choice remains visible.

## Expected Shortfall

Expected Shortfall measures average loss conditional on being beyond the VaR threshold.

It complements VaR by describing tail severity rather than only the percentile boundary.
