# VaR Backtesting

## Business interpretation

A VaR model should not be trusted only because its formula looks reasonable.

The project tests the model against realized observations.

For each day:

```text
Use the previous 250 P&L observations
    -> estimate 99% VaR
    -> observe the next day's realized P&L
    -> record an exception if loss > VaR
```

This is an out-of-sample workflow because the next-day P&L is not used to calculate its own VaR forecast.

## Expected exceptions

A 99% VaR model implies an expected exception probability of approximately 1%.

Over 500 test days, a rough expectation is about five exceptions. The exact number will vary randomly.

## Kupiec unconditional-coverage test

The Kupiec test asks:

> Is the total number of observed exceptions statistically consistent with the expected exception rate?

A very small p-value suggests the coverage may be inconsistent with the stated confidence level.

## Christoffersen independence test

Exception counts alone are not enough.

A model could generate the correct number of exceptions but have them occur in clusters during volatile periods.

The Christoffersen independence test asks whether exceptions appear independent through time.

## Interpretation

Failing a backtest does not automatically identify the cause.

Potential causes include:

- changing volatility,
- stale calibration,
- correlation shifts,
- fat tails,
- bad market data,
- incorrect positions,
- model assumptions that no longer fit the book.

A Market Risk analyst should investigate rather than mechanically "fix" the model to pass a test.
