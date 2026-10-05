# VaR and Expected Shortfall Models

## 1. Historical VaR

Historical VaR sorts prior portfolio P&L observations and reads the lower-tail percentile.

For 99% confidence:

```text
VaR = positive magnitude of the 1st percentile of historical P&L
```

### Strengths

- simple to explain,
- preserves historical nonlinear distribution shape in the P&L series,
- no normality assumption.

### Weaknesses

- limited to events present in the historical window,
- equal-weight history can react slowly to volatility changes,
- sensitive to window selection.

## 2. Parametric normal VaR

The model estimates mean and standard deviation of portfolio P&L and assumes a normal distribution.

```text
P&L quantile = mean + z × sigma
VaR = -lower-tail quantile
```

### Strengths

- fast,
- transparent,
- easy to attribute using covariance.

### Weaknesses

- normality can underrepresent fat tails,
- may not react well to volatility regimes,
- unsuitable for nonlinear portfolios without additional modeling.

## 3. Monte Carlo VaR

The current implementation simulates many daily portfolio P&L observations from the fitted normal distribution.

This is intentionally a teaching baseline. A production implementation could simulate correlated market risk factors, stochastic volatility, jumps, options repricing, and other nonlinear effects.

## 4. Expected Shortfall

Expected Shortfall averages the losses in the tail beyond the VaR threshold.

Conceptually:

```text
ES = average loss conditional on loss being at or beyond VaR
```

It is useful because VaR gives a threshold but does not say how severe losses can be once the threshold has been exceeded.

## 5. Weighted Historical VaR

The project uses exponential probability weights:

```text
recent observations -> larger weight
older observations  -> smaller weight
```

The objective is to demonstrate a simple way to make a historical model more responsive to current volatility.

The decay factor is a model assumption and must be documented and validated rather than chosen solely because it improves one backtest.
