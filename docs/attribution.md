# Risk Attribution

Portfolio VaR is more useful when its drivers can be explained.

The project allocates Normal Parametric VaR across positions using each position's covariance with total portfolio P&L.

A positive component contribution increases portfolio VaR under the estimated covariance structure. A negative contribution indicates diversification.

Component contributions sum to total Parametric VaR up to floating-point tolerance.

A negative contribution should not be interpreted as a permanently protective position. Correlations, volatilities, and liquidity conditions can change, which is why attribution is reviewed alongside stress testing and validation.
