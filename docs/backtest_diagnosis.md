# Why did the VaR backtest fail?

The initial public-data sample recorded 42 historical-VaR exceptions in 1,954 forecasts (2.15%, against a 1% target). This follow-up keeps the same price snapshot and financial hedge book. It tests volatility scaling and a calendar-based roll sensitivity without deleting realized losses.

## What is supported by the data

Using the first three and last two Monday–Friday weekdays of each month, 14 of 42 exceptions (33.3%) fall in the band, compared with 22.7% of forecast dates. This calendar ignores exchange holidays. Alternative two/three-day bands are saved in `calendar_diagnostic.csv`. The approximate enrichment is real in this sample, but its descriptive Fisher p-value is 0.134 and exceptions are serially dependent, so the simple table is not a causal or definitive statistical test of roll contamination.

The largest RB changes and portfolio losses are saved with leg contributions for review. Month turns are **possible roll flags**, not proven Yahoo switch dates. Seasonal grade changes, real market events, and contract switches require dated contracts to separate. No proxy price has been “corrected” merely because it is large or near a month boundary.

The baseline has 7 exceptions in 2020, 12 in 2022 and 12 in 2026, alongside 6 in 2025. Volatility regimes and serial dependence therefore deserve attention even before contract data is available.

## Fair comparison

FHS initializes volatility from 60 past observations, then requires 250 standardized shocks. All compared methods therefore use the same **1,894 forecast dates**. On this common sample the ordinary historical benchmark has 41 exceptions (2.16%), rather than comparing a new model to a different original sample.

| Model | Exceptions | Rate | Coverage p | Independence p |
|---|---:|---:|---:|---:|
| Historical, common dates | 41 | 2.16% | 0.000010 | <0.000001 |
| Historical, calendar flags excluded from training only | 47 | 2.48% | <0.000001 | <0.000001 |
| EWMA FHS, decay 0.94 | 27 | 1.43% | 0.080 | 0.0058 |
| EWMA FHS 0.94, calendar flags excluded from training | 33 | 1.74% | 0.0033 | 0.0197 |

The primary 0.94 EWMA filter improves unconditional coverage, but **still fails independence and joint conditional coverage** over the full common sample. Average VaR rises from about $91,609 to $121,020, so the improvement comes with higher estimated risk. It is not a free improvement or a production validation pass.

On the retrospective 2024-onward segment, baseline exceptions fall from 19/696 (2.73%) to 12/696 (1.72%) under FHS; conditional-coverage p is 0.095 for FHS. This segment has already been inspected and is not an untouched holdout. Fixed 0.97 and 0.99 decay sensitivities are reported too; no parameter is automatically chosen to maximize a p-value.

## Filter construction

The recursion is `sigma[t]^2 = lambda*sigma[t-1]^2 + (1-lambda)*pnl[t-1]^2`, with zero conditional mean. Each historical residual is `pnl[j]/sigma[j]`, using volatility known before observation j. A forecast rescales the previous 250 residuals by today's prior-only sigma and takes the historical loss quantile. This is a fixed-book portfolio P&L filter, not a factor-level dynamic-correlation model.

The calendar-exclusion sensitivity omits flagged observations from the *estimation window only*. It still scores all subsequent dates, including flagged losses. It performs worse here, so removing calendar observations is not adopted as a fix. Filtering does not repair vendor roll construction either.

## Reproduce and audit

```bash
python run_diagnostics.py
```

Inputs default to the exact committed live sample. `outputs/diagnosis_2026-10/` contains a checksum, calendar sensitivity, yearly exceptions, largest RB moves, leg-level loss attribution, model comparisons, exception ledger and a gzip-compressed full forecast file. Tests change future P&L to prove earlier forecasts do not move, verify the volatility recursion, and verify that calendar exclusions do not remove realized losses.

The next gate is observed dated-contract reconciliation and prospective monitoring on new data. The evidence supports “volatility scaling reduced undercoverage, while dependence remains,” not “roll jumps caused the failure and it is now fixed.”
