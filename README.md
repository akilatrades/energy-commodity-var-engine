# Energy Commodity Portfolio VaR & Market Risk Analytics

[![tests](https://github.com/akilatrades/energy-commodity-var-engine/actions/workflows/tests.yml/badge.svg)](https://github.com/akilatrades/energy-commodity-var-engine/actions/workflows/tests.yml)

Python-based market-risk framework for an illustrative energy futures portfolio. The project compares multiple Value at Risk (VaR) methods, calculates Expected Shortfall, attributes risk by position, runs stress scenarios, backtests model exceptions, and monitors an illustrative risk limit.

> **One-line summary:** build a daily market-risk view of an energy futures book and test whether the reported risk measures are reasonable, stable, and useful for decision-making.

## 5-minute professional review

1. Read the **Business question** and **What the project measures** sections below.
2. Open `outputs/executive_summary.md` after running the project for a management-style risk summary.
3. Review `notebooks/01_portfolio_and_pnl.ipynb` for the beginner-friendly starting point.
4. Review `docs/backtesting.md` and `docs/limitations.md` to see how model risk is handled.
5. Inspect `src/` and `tests/` for reusable logic and automated validation.

**Skills demonstrated:** market risk, Value at Risk, Expected Shortfall, commodity futures, risk attribution, stress testing, limit monitoring, backtesting, Python, pandas, NumPy, SciPy, pytest, and GitHub Actions.

## Business question

A trading book can contain positions that gain and lose value for different reasons. A Market Risk team needs to answer questions such as:

- How much can the portfolio lose on a bad day under the model assumptions?
- Which positions are driving that risk?
- Are some positions offsetting others?
- How does the book behave under predefined stress scenarios?
- Is the VaR model producing too many exceptions?
- Are risk measures within approved limits?
- Can the result be explained clearly to traders and senior management?

This repository builds a simplified framework around those questions.

## Illustrative portfolio

The default portfolio contains linear futures exposures to:

| Symbol | Market | Example contract multiplier |
|---|---|---:|
| `CL=F` | WTI crude oil | 1,000 bbl |
| `RB=F` | RBOB gasoline | 42,000 gal |
| `HO=F` | Heating oil | 42,000 gal |
| `NG=F` | Henry Hub natural gas | 10,000 MMBtu |

The positions are examples for analytics only. They are not trade recommendations.

## What the project measures

### 1. Daily position and portfolio P&L

For a linear futures position:

```text
Daily P&L
= number of contracts
× contract multiplier
× daily price change
```

The project calculates P&L separately by position and then sums the positions into total portfolio P&L.

### 2. Historical VaR

Historical VaR uses the actual historical P&L distribution.

At 99% confidence, the model asks:

> What loss threshold was exceeded on roughly 1% of the historical observations?

No normal-distribution assumption is required.

### 3. Parametric VaR

Parametric VaR assumes the P&L distribution can be approximated by a normal distribution using the estimated mean and standard deviation.

It is simple and fast, but it can understate risk when returns have fat tails, volatility clustering, or other non-normal behavior.

### 4. Monte Carlo VaR

The project simulates many possible daily P&L observations from an estimated distribution and calculates the percentile loss from the simulated outcomes.

The current implementation is deliberately simple: it uses a fitted normal P&L distribution. A production model could instead simulate risk factors, volatility dynamics, nonlinear instruments, and correlations directly.

### 5. Expected Shortfall

VaR identifies a loss threshold. Expected Shortfall asks:

> If the loss is already worse than VaR, how large are those tail losses on average?

This provides more information about the severity of extreme observations.

### 6. Weighted historical VaR

Plain historical VaR gives each historical observation equal probability.

The project also includes an exponentially weighted historical method so that recent observations receive more weight than older observations.

This is useful for demonstrating why a risk analyst may want a model to react faster when volatility changes.

### 7. Component VaR / risk attribution

A portfolio-level VaR number is not enough for management.

The project estimates each position's contribution to parametric VaR and identifies whether a position:

- contributes positively to total risk, or
- provides diversification and reduces total portfolio risk.

### 8. Stress testing

The framework applies deterministic scenarios such as:

- broad energy selloff,
- crude rally with refined products lagging,
- refined-products squeeze,
- natural-gas shock.

Stress tests answer a different question from VaR: they show what happens under specific moves rather than relying on a percentile of historical/modelled behavior.

### 9. VaR backtesting

The project estimates VaR using only prior observations and compares the next realized P&L against the forecast.

It records a **VaR exception** when:

```text
Realized P&L < -VaR
```

The backtesting layer includes:

- exception counts,
- actual versus expected exception rate,
- Kupiec unconditional-coverage test,
- Christoffersen exception-independence test.

### 10. Risk-limit monitoring

The project compares the current VaR result with an illustrative limit and reports:

- current risk value,
- limit,
- utilization percentage,
- `OK`, `WATCH`, or `BREACH` status.

This demonstrates the control side of Market Risk in addition to model calculation.

## Architecture

```text
Market prices
    |
    v
Illustrative futures positions
    |
    v
Daily position P&L
    |
    +--> Historical VaR / ES
    +--> Parametric VaR / ES
    +--> Monte Carlo VaR / ES
    +--> Weighted historical VaR
    |
    +--> Component VaR attribution
    +--> Stress scenarios
    +--> Rolling VaR backtest
    +--> Kupiec / Christoffersen tests
    +--> Risk-limit utilization
    |
    v
Management-style executive summary
```

## Repository structure

```text
.
├── README.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── run_analysis.py
├── src/
│   ├── data.py
│   ├── portfolio.py
│   ├── var_models.py
│   ├── attribution.py
│   ├── stress.py
│   ├── backtesting.py
│   ├── limits.py
│   └── reporting.py
├── docs/
│   ├── methodology.md
│   ├── var_models.md
│   ├── attribution.md
│   ├── stress_testing.md
│   ├── backtesting.md
│   ├── limits.md
│   ├── limitations.md
│   ├── data_dictionary.md
│   └── glossary.md
├── data/
├── notebooks/
├── outputs/
└── tests/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
python run_analysis.py --mode demo
```

### Demo mode

`--mode demo` uses a deterministic synthetic energy dataset so the full workflow can run offline.

Every result generated from demo mode must be treated as **synthetic demonstration output**, not historical market evidence.

### Live mode

```bash
python run_analysis.py --mode live
```

Live mode attempts to download public continuous futures proxies from Yahoo Finance.

Public continuous series are useful for portfolio research, but they are not equivalent to the market data, contract mappings, curves, and valuation systems used by a production Market Risk function.

## Generated outputs

The analysis writes:

- `portfolio_positions.csv`
- `daily_position_pnl.csv`
- `var_method_comparison.csv`
- `component_var.csv`
- `stress_scenarios.csv`
- `historical_var_backtest.csv`
- `backtest_summary.csv`
- `limit_monitoring.csv`
- `portfolio_pnl_history.svg`
- `var_backtest.svg`
- `component_var.svg`
- `executive_summary.md`

See `outputs/README.md` for the reporting layer.

## Model governance philosophy

A calculated VaR number is not automatically a good risk measure.

The project therefore separates four questions:

1. **Measurement** — what does each model say the risk is?
2. **Attribution** — which positions are creating or reducing the risk?
3. **Validation** — does the model produce a reasonable exception pattern?
4. **Control** — is the reported risk within an illustrative approved limit?

That separation is intentional because Market Risk is not only a modeling function; it also requires independent review, escalation, and clear communication.

## Important limitations

This is a portfolio and learning project, not a bank production risk engine.

The current model simplifies or excludes:

- nonlinear options and Greeks,
- intraday risk,
- exact exchange contract rolls,
- independent market-data verification,
- FX conversion across currencies,
- liquidity and concentration add-ons,
- credit and counterparty risk,
- initial/variation margin,
- P&L explain,
- new-product approval,
- full model-governance controls,
- production ETRM / trading-system integration.

See `docs/limitations.md` for the full discussion.

## Why this project exists

The goal is not to produce the most complicated VaR model possible.

The goal is to demonstrate a clear Market Risk workflow:

> understand the positions, calculate the risk, explain the drivers, stress the book, test the model, monitor the limit, and communicate the result.

Educational and portfolio use only. Not investment advice.
