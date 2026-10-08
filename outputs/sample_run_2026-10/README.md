# Point-in-time risk sample

**Public-data historical sample; not a forecast or live risk feed.**

Last price date: 2026-10-07. Generation timestamp and input checksum are in `analysis_metadata.json`.

The book is +30 CL, -20 RB and -10 HO contracts: a refiner's financial hedge of a 30,000-bbl 3-2-1 margin exposure. Physical margin is excluded. A hedge loss can offset a physical gain.

Read `executive_summary.md`, `var_method_comparison.csv`, `var_backtest_summary.csv`, and the stress tables. `var_backtest.svg` plots forecasts against subsequent P&L. Exact prices and configuration are saved here.

The Yahoo continuous proxies have unknown roll construction. The contract-panel roll builder is a separate, tested module and has not been applied to these proxy prices.
