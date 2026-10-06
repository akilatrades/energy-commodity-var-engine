# Energy Commodity Portfolio VaR & Market Risk Analytics

[![tests](https://github.com/akilatrades/energy-commodity-var-engine/actions/workflows/tests.yml/badge.svg)](https://github.com/akilatrades/energy-commodity-var-engine/actions/workflows/tests.yml)

Python market-risk framework for a linear energy futures portfolio. The project converts position-level market moves into daily P&L, compares multiple VaR methodologies, measures Expected Shortfall, attributes portfolio risk, runs hypothetical and historical stress tests, validates VaR forecasts out of sample, and monitors limit utilization.

## Current results / repository status

The project is currently configured around an illustrative energy futures portfolio with **40 CL**, **-15 RB**, **-12 HO**, and **35 NG** contracts.

| Item | Current configuration / result |
|---|---|
| Risk horizon | 1 trading day |
| Confidence level | 99% |
| Current risk window | 250 observations |
| Monte Carlo | 50,000 correlated Student-t simulations, 6 degrees of freedom |
| Weighted Historical decay | 0.97 |
| VaR limit | $500,000 |
| Validation | Rolling out-of-sample Historical, Parametric, and Weighted Historical VaR with Kupiec and Christoffersen tests |
| Stress framework | Broad energy selloff, crude rally/products lag, refined-products squeeze, and natural-gas shock |

The repository currently validates the **full analytical pipeline**—position P&L, VaR / Expected Shortfall, attribution, stress testing, backtesting, calibration sensitivity, limit monitoring, and executive reporting.

A static live historical risk snapshot is **not committed to the repository by design**. Generated live and demo outputs are ignored so synthetic results are never presented as historical findings and time-sensitive public-proxy results are not mistaken for a permanent risk statement. Running `python run_analysis.py --mode live` generates the current public-proxy results locally.

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
