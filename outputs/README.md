# Generated Results

Run:

```bash
python run_analysis.py --mode demo
```

or:

```bash
python run_analysis.py --mode live
```

The project writes the following reporting layer.

## Portfolio

- `portfolio_positions.csv` — position definitions.
- `daily_position_pnl.csv` — daily P&L by position and total portfolio.

## VaR / Expected Shortfall

- `var_method_comparison.csv` — Historical, Parametric, Monte Carlo, and weighted historical VaR comparison.

## Risk attribution

- `component_var.csv` — parametric component VaR by position, including diversification flags.

## Stress testing

- `stress_scenarios.csv` — position and total P&L under deterministic shocks.

## Backtesting

- `historical_var_backtest.csv` — daily rolling historical VaR forecasts, realized P&L, and exception flags.
- `backtest_summary.csv` — Kupiec coverage and Christoffersen independence diagnostics.

## Limits

- `limit_monitoring.csv` — illustrative VaR limit, utilization, and status.

## Management summary

- `executive_summary.md` — concise senior-management style risk summary.

## Charts

- `portfolio_pnl_history.svg`
- `var_backtest.svg`
- `component_var.svg`

If the project was run in demo mode, all generated outputs are synthetic demonstration results and should be labeled accordingly.
