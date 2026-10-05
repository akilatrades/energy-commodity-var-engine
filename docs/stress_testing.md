# Stress Testing

## Hypothetical scenarios

Hypothetical percentage shocks are stored in **config/stress_scenarios.csv** rather than hard-coded in the calculation engine.

The default set includes a broad energy selloff, crude rally with products lagging, refined-products squeeze, and natural-gas shock.

Each scenario is translated through current linear futures sensitivities into position and total portfolio P&L.

## Historical replay

Historical replay identifies the worst observed fixed-book P&L days in the analyzed sample and reports the market moves that occurred on those dates.

This provides an empirical complement to hypothetical scenarios.

## Interpretation

VaR and stress testing answer different questions.

VaR is a percentile-based model estimate. Stress testing evaluates explicitly defined or historically observed market moves.

Neither should be treated as a substitute for the other.

## Production extensions

A production stress framework could add liquidity stresses, basis and calendar-spread shocks, options volatility shocks, concentration scenarios, reverse stress testing, desk-specific historical episodes, and governance around scenario approval and review.
