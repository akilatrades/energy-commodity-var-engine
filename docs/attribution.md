# Risk Attribution

## Why attribution matters

A senior risk report should not stop at:

> Portfolio VaR = $X

A risk manager also needs to understand what is driving the number.

## Component VaR

For the current linear normal model, component VaR is based on each position's covariance with the total portfolio.

A positive component VaR means the position contributes risk.

A negative component VaR means the position is acting as a diversifier under the estimated covariance structure.

The component contributions sum to total parametric VaR, up to rounding.

## Interpretation caution

A negative contribution does not mean the position is "safe."

The diversification relationship can change when:

- correlations shift,
- volatility changes,
- liquidity deteriorates,
- market structure breaks down.

That is why attribution should be viewed alongside stress testing and backtesting.
