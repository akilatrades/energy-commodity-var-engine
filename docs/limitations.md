# Model Limitations

A professional risk project should state clearly what the model does not capture.

## Instrument limitations

The current book contains linear futures only.

It does not model:

- options,
- delta/gamma/vega/theta,
- swaps with complex settlement conventions,
- structured products,
- path-dependent derivatives.

## Market-data limitations

Live mode uses public continuous futures proxies.

These are not equivalent to production market data because a real environment would require:

- exact contract identifiers,
- exchange settlement sources,
- roll calendars,
- independent price verification,
- timestamps and stale-price controls,
- corporate data governance.

## VaR limitations

Historical VaR can miss events absent from the historical window.

Parametric and Monte Carlo normal VaR assume a distribution that can understate fat-tail behavior.

Weighted historical VaR introduces a decay parameter that itself creates model risk.

No VaR method should be interpreted as a maximum possible loss.

## Portfolio limitations

The project excludes:

- intraday position changes,
- FX conversion,
- basis and location mapping,
- calendar-spread risk decomposition,
- liquidity risk,
- concentration add-ons,
- margin and funding,
- transaction costs.

## Backtesting limitations

A backtest can diagnose a problem without identifying its root cause.

Exception counts can also be noisy in small samples, especially at 99% confidence because exceptions are intentionally rare.

## Production-control gap

A real bank or trading company would require controls around:

- trade capture,
- valuations,
- sensitivities,
- risk-factor mapping,
- data quality,
- P&L explain,
- risk limits,
- approvals,
- audit trails,
- model governance,
- change management,
- access control,
- regulatory reporting where applicable.

This repository is a learning and portfolio project rather than a production Market Risk platform.
