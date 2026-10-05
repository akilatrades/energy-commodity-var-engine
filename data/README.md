# Data

The project supports two data modes.

## Demo mode

`python run_analysis.py --mode demo`

Generates a deterministic synthetic dataset with correlated and mildly clustered energy-market volatility. This exists for reproducibility and offline learning.

**Synthetic results must never be described as historical market findings.**

## Live mode

`python run_analysis.py --mode live`

Attempts to download public continuous futures proxies through Yahoo Finance:

- `CL=F` — WTI crude oil
- `RB=F` — RBOB gasoline
- `HO=F` — heating oil
- `NG=F` — Henry Hub natural gas

These series are convenient public proxies. They are not equivalent to contract-specific market data from a production trading or risk system.

A production framework would require validated instrument identifiers, official settlements, roll logic, contract calendars, timestamps, independent price verification, and data-quality controls.
