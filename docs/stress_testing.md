# Stress Testing

## Why stress testing is different from VaR

VaR is a percentile-based model result.

Stress testing asks a direct scenario question:

> What would the portfolio P&L be if specified markets moved by specified amounts?

The two tools answer different questions and should complement each other.

## Default scenarios

The project includes illustrative scenarios:

- broad energy selloff,
- crude rally / products lag,
- refined-products squeeze,
- natural-gas shock.

Each shock is applied to the latest price and translated into position P&L using the futures contract multiplier and contract count.

## Production use

A professional stress program would include:

- historically observed scenarios,
- hypothetical scenarios,
- desk-specific concentrations,
- cross-market dislocations,
- liquidity stresses,
- basis and curve shocks,
- options volatility shocks,
- reverse stress testing.
