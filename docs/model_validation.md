# Model Validation

## Out-of-sample design

For each test date, the model uses only the preceding estimation window to calculate VaR. The next realized P&L is then compared with that forecast.

An exception occurs when realized P&L is below negative VaR.

This prevents the observation being tested from contributing to its own forecast.

## Models tested

The validation comparison covers:

- Historical VaR
- Parametric Normal VaR
- Weighted Historical VaR

Monte Carlo is reported in the risk-method comparison but is not currently included in the rolling backtest because re-estimating and simulating tens of thousands of scenarios for every test date would materially increase runtime. That trade-off is explicit rather than hidden.

## Coverage

The Kupiec unconditional-coverage test evaluates whether the total exception frequency is consistent with the stated confidence level.

At 99% confidence, the expected exception probability is 1%.

## Independence

The Christoffersen independence test evaluates whether exceptions appear clustered through time.

A model can produce the correct total number of exceptions and still fail to react appropriately to volatility if those exceptions cluster.

## Conditional coverage

The project also reports a combined conditional-coverage statistic by adding the coverage and independence likelihood-ratio statistics and evaluating the result against a chi-square distribution with two degrees of freedom.

## Calibration sensitivity

Validation is repeated across alternative estimation windows and, for Weighted Historical VaR, alternative decay factors.

The project does not automatically choose whichever parameter combination gives the highest p-value. Sensitivity analysis is intended to show model stability and calibration dependence, not to optimize away unfavorable evidence.

## Interpretation

A failed validation diagnostic does not identify the root cause. Investigation may include volatility regime change, changing correlations, fat tails, insufficient history, stale calibration, market-data issues, position mapping, or model assumptions that are not appropriate for the portfolio.

Validation informs model review rather than mechanically approving or rejecting a model.
