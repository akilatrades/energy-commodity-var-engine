# Full-revaluation option risk

`src/nonlinear.py` supports European option legs on one futures risk factor, plus a signed linear futures-equivalent exposure. Quantities are barrels. Each historical absolute price change is applied to today’s forward, each option ages by 1/252 year, and its Black-76 value is recomputed. Scenario P&L is the new value minus the initial value plus linear exposure times the price change.

`run_option_risk.py` uses a 100,000-bbl long WTI proxy with an 85%-of-forward put floor. The three-way structure sells a put at 65% of the initial forward. Both ceilings are solved for zero net premium using assumed 40% volatility, 4% rate and one year. The example is **separate from the refiner book**, whose business exposure has different signs.

The last 250 absolute CL changes become equally weighted historical scenarios. With no `--prices` input, changes come from the deterministic synthetic demo and are labeled as such. An optional `--prices` public snapshot must have `date` and `CL=F` columns. VaR and ES use the same historical functions as the linear model.

Volatility is held fixed, so this captures price nonlinearity and time decay but not historical joint price/volatility risk. An absolute volatility shift can be supplied to the revaluation function for stress testing. A one-factor option model does not include cross-commodity correlation. Do not add its standalone VaR mechanically to refiner VaR.

Nonpositive shocked forwards are rejected because lognormal Black-76 cannot price them. A horizon beyond option expiry is also rejected because the settlement path is missing. A normal or appropriately shifted model is needed for negative-price states. American exercise, average-price options, smile and dealer quotes are not modeled.

Tests use put-call parity at expiry to independently reconcile an option combination to linear futures P&L, and reject invalid negative-price states and missing settlement paths.
