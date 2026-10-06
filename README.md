# Energy Commodity Portfolio VaR & Market Risk Analytics

[![tests](https://github.com/akilatrades/energy-commodity-var-engine/actions/workflows/tests.yml/badge.svg)](https://github.com/akilatrades/energy-commodity-var-engine/actions/workflows/tests.yml)

Python market-risk framework for a linear energy futures portfolio. The project converts position-level market moves into daily P&L, compares multiple VaR methodologies, measures Expected Shortfall, attributes portfolio risk, runs hypothetical and historical stress tests, validates VaR forecasts out of sample, and monitors limit utilization.

> **Project status:** Version 1.0 is complete. The core analytical scope is frozen as a stable release; future changes will focus on maintenance, data refreshes, or targeted extensions when they add clear value.

## Current results / repository status

The project currently uses an example portfolio of energy futures:

- **40 WTI crude oil contracts**
- **short 15 RBOB gasoline contracts**
- **short 12 heating-oil contracts**
- **35 Henry Hub natural-gas contracts**

"Short" means the example portfolio benefits when that futures price falls and loses when it rises.

| Setting | Plain-English meaning | Current value |
|---|---|---:|
| Risk horizon | How far ahead the model measures risk | 1 trading day |
| Confidence level | The model focuses on losses expected to be exceeded only about 1% of the time | 99% |
| Historical window | Number of recent market observations used for the main risk estimate | 250 |
| Monte Carlo simulation | Number of simulated market scenarios used in one of the risk models | 50,000 |
| Weighted-history setting | Gives more importance to recent market moves than older ones | 0.97 decay |
| VaR limit | Example maximum one-day risk limit used by the project | $500,000 |

### What the project currently does

The pipeline can calculate daily portfolio profit and loss, estimate **Value at Risk (VaR)**, estimate **Expected Shortfall**, show which positions contribute most to risk, run severe market scenarios, test whether the VaR model performed reasonably on past data, and compare the result with a predefined risk limit.

In simple terms:

- **VaR** asks: "How large could a bad one-day loss be under normal model assumptions?"
- **Expected Shortfall** asks: "If losses are worse than the VaR threshold, how large are those bad losses on average?"
- **Stress testing** asks: "What happens if markets move sharply in a specific scenario?"
- **Backtesting** checks whether the model's past risk forecasts matched what actually happened often enough.

The project tests four example stress scenarios: a broad energy selloff, a crude-oil rally where refined products lag, a refined-products price squeeze, and a natural-gas price shock.

A fixed live historical risk number is **not saved in the repository on purpose**. Live results change as market data changes, and the project also has a synthetic demo mode. Keeping generated results out of GitHub prevents a demo number from being mistaken for a real historical result. Running `python run_analysis.py --mode live` creates the latest public-data version locally.

## Scope

The reference portfolio contains WTI crude oil, RBOB gasoline, heating oil, and Henry Hub natural gas futures.

The analytical workflow is:

~~~text
Positions
  -> Daily P&L
  -> VaR / Expected Shortfall
  -> Risk Attribution
  -> Stress Testing
  -> Model Validation
  -> Limit Monitoring
  -> Executive Risk Summary
~~~

The objective is not to maximize model complexity. It is to show a controlled, explainable Market Risk process in which the risk number, its drivers, the model assumptions, and the validation results can all be reviewed independently.

## Risk framework

| Area | Implementation |
|---|---|
| P&L | Linear futures P&L by position and total portfolio |
| Historical risk | 99% Historical VaR and Expected Shortfall |
| Parametric risk | Normal-theory VaR and Expected Shortfall |
| Monte Carlo | Correlated Student-t risk-factor simulation |
| Responsive history | Exponentially weighted Historical VaR |
| Attribution | Parametric component VaR by position |
| Stress | Configurable hypothetical shocks plus historical replay |
| Validation | Rolling out-of-sample forecasts, Kupiec coverage, Christoffersen independence |
| Sensitivity | Alternative lookback windows and decay factors |
| Controls | Configurable VaR limit and utilization status |
| Reporting | Management-style executive summary and reproducible CSV outputs |

## Portfolio configuration

Position assumptions are separated from calculation code in **config/portfolio.csv**.

| Symbol | Market | Contract multiplier |
|---|---|---:|
| CL=F | WTI crude oil | 1,000 bbl |
| RB=F | RBOB gasoline | 42,000 gal |
| HO=F | Heating oil | 42,000 gal |
| NG=F | Henry Hub natural gas | 10,000 MMBtu |

Hypothetical stress scenarios, model parameters, and risk limits are also stored under **config/** so they can be reviewed without changing Python source code.

## Data

Historical mode uses public Yahoo Finance continuous futures proxies. These are suitable for portfolio research and model demonstration, but they are not equivalent to a production trading firm's contract-level settlement data.

The project explicitly treats them as **public continuous futures proxies**, not as an exchange-grade risk feed. Roll construction, exact contract mapping, independent price verification, and production market-data controls are outside the scope of this repository.

Demo mode generates deterministic synthetic data for offline reproducibility and CI smoke testing. Synthetic results are not presented as historical findings.

## Repository structure

~~~text
.
├── config/
│   ├── model_config.json
│   ├── portfolio.csv
│   ├── risk_limits.json
│   └── stress_scenarios.csv
├── data/
├── docs/
├── notebooks/
├── outputs/
├── src/
│   ├── attribution.py
│   ├── backtesting.py
│   ├── data.py
│   ├── limits.py
│   ├── portfolio.py
│   ├── reporting.py
│   ├── stress.py
│   └── var_models.py
├── tests/
├── run_analysis.py
├── pyproject.toml
└── requirements.txt
~~~

## Reproduce the analysis

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python run_analysis.py --mode live
~~~

Windows activation:

~~~text
.venv\Scripts\activate
~~~

For an offline deterministic smoke test:

~~~bash
python run_analysis.py --mode demo
~~~

Generated results are written to **outputs/** and include method comparison, component VaR, hypothetical and historical stress results, model-validation summaries, calibration sensitivity, limit utilization, charts, metadata, and an executive summary.

## Model validation

The project does not treat a VaR estimate as valid simply because the formula runs.

Historical, Parametric, and Weighted Historical VaR are evaluated using rolling out-of-sample forecasts. Validation reports exception counts, expected versus realized exception rates, Kupiec unconditional coverage, Christoffersen independence, and conditional coverage. A separate sensitivity table shows how results change across reasonable lookback windows and decay factors without automatically selecting whichever specification produces the most favorable backtest.

## Governance and limitations

This repository is an analytical portfolio project, not a production Market Risk platform.

Important exclusions include nonlinear options and Greeks, intraday position changes, official exchange settlement feeds, independent market-data verification, exact futures roll mapping, liquidity and concentration add-ons, margin and funding, P&L explain, counterparty credit risk, formal model approval, and production trading-system integration.

See **docs/limitations.md** for the full model-use boundary and **docs/model_validation.md** for the validation framework.

Educational and portfolio use only. Not investment advice.
