# Why did the VaR backtest fail?

The original historical model records 42 exceptions in 1,954 forecasts (2.15%, against a 1% target). On matching dates, EWMA filtered historical simulation cuts that rate to **1.43% and passes the 5% coverage test**. The investigation separates volatility clustering from problems in the proxy's contract exposure.

## April 20, 2020: the exception to explain first

The saved Yahoo `CL=F` series follows the expiring May WTI contract from $18.27 to **−$37.63/bbl** on April 20, one day before expiry. The [CFTC account](https://www.cftc.gov/PressRoom/SpeechesTestimony/berkovitzstatement050720) describes the collapse amid the pandemic demand shock and scarce available Cushing storage. At +30,000 barrels, the $55.90 fall creates a **$1.677M CL loss**; product-leg gains reduce the total-book loss to **$1.613M, or 22.5× the $71,778 historical VaR**. A refiner hedge policy that rolls before expiry would already hold another delivery month and avoid this specific May-contract collapse. For that policy, the proxy misrepresents the intended exposure: the missing roll convention is the data-construction problem, while the negative settlement itself was real. The exception remains in every reported comparison.

[Saved loss attribution](../outputs/diagnosis_2026-10/largest_losses_by_leg.csv)

## Month turns and volatility clusters

Using the first three and last two Monday–Friday weekdays of each month, 14 of 42 exceptions (33.3%) fall in the band, against 22.7% of forecast dates. The calendar ignores exchange holidays; alternative bands are saved in `calendar_diagnostic.csv`. The descriptive Fisher p-value is 0.134, so this is a lead for contract-level investigation rather than proof of roll contamination.

The largest RB changes and portfolio losses are saved with leg contributions. Month turns flag candidate contract switches or seasonal grade effects for review. The baseline also has 7 exceptions in 2020, 12 in 2022 and 12 in 2026, alongside 6 in 2025. That clustering motivates volatility scaling.

## Fair comparison

FHS initializes volatility from 60 past observations, then requires 250 standardized shocks. All compared methods therefore use the same **1,894 forecast dates**. The historical benchmark has 41 exceptions (2.16%) on those dates.

| Model | Exceptions | Rate | Coverage p | Independence p |
|---|---:|---:|---:|---:|
| Historical, common dates | 41 | 2.16% | 0.000010 | <0.000001 |
| Historical, calendar flags excluded from training | 47 | 2.48% | <0.000001 | <0.000001 |
| EWMA FHS, decay 0.94 | 27 | 1.43% | 0.0802 | 0.0058 |
| EWMA FHS 0.94, calendar flags excluded from training | 33 | 1.74% | 0.0033 | 0.0197 |

At the 5% threshold, the primary 0.94 filter **passes unconditional coverage but fails independence and joint conditional coverage**. Average VaR rises from $91,609 to $121,020. The model responds more strongly to changing risk, but exceptions still cluster.

On the retrospective 2024-onward segment, baseline exceptions fall from 19/696 (2.73%) to 12/696 (1.72%) under FHS; its conditional-coverage p-value is 0.095. Fixed 0.97 and 0.99 decay sensitivities are reported alongside the primary model.

## Why the primary decay is 0.94

RiskMetrics' [1996 Technical Document, §5.3.2, printed pp. 97–100](https://www.msci.com/documents/10199/5915b101-4206-4ba0-aee2-3449d5c7e95a) uses 0.94 for daily EWMA volatility and 0.97 for monthly data. This project uses that conventional daily baseline in its portfolio-P&L filter. The [initial implementation](https://github.com/akilatrades/energy-commodity-var-engine/blob/9a96c1594173d8de0b7af4895c91f8188bb141d6/run_diagnostics.py) explicitly fixes 0.94 as primary and reports 0.97 and 0.99 as sensitivities, with no p-value-based selection step. That designation is visible before the committed automated result run; the historical exercise remains retrospective rather than a preregistered holdout test.

| Daily EWMA decay | Weight on latest squared P&L | Weight half-life (observations) | Exceptions / 1,894 | Coverage p | Pass at 5%? |
|---|---:|---:|---:|---:|---|
| **0.94 — primary** | 6% | 11.2 | 27 | 0.0802 | Yes |
| 0.97 — sensitivity | 3% | 22.8 | 29 | 0.0312 | No |
| 0.99 — sensitivity | 1% | 69.0 | 39 | 0.000050 | No |

Half-life is `ln(0.5) / ln(decay)`. The larger decays retain volatility history longer and react more slowly to a new shock. Both are applied to daily observations here, so they test responsiveness rather than a different forecast horizon. All sensitivity results are retained, including failures; the 0.94 coverage pass does not establish an optimal decay or resolve independence.

## Filter construction

The recursion is `sigma[t]^2 = lambda*sigma[t-1]^2 + (1-lambda)*pnl[t-1]^2`, with zero conditional mean. Each historical residual is `pnl[j]/sigma[j]`, using volatility known before observation j. A forecast rescales the previous 250 residuals by today's prior-only sigma and takes the historical loss quantile.

The calendar sensitivity excludes flagged dates from the estimation window only and scores every subsequent loss. It performs worse, so calendar exclusion is not adopted. The [real dated-contract demonstration](continuous_series.md) addresses roll reconciliation separately.

## Reproduce and audit

```bash
python run_diagnostics.py
```

`outputs/diagnosis_2026-10/` contains the input checksum, calendar sensitivity, yearly exceptions, largest RB moves, loss attribution, model comparisons, exception ledger and compressed forecasts. Tests verify the volatility recursion, prove future P&L cannot change earlier forecasts, and check that training exclusions retain realized losses.

The next steps are expired-contract reconstruction under an explicit roll policy and prospective monitoring of FHS. [Limitations](limitations.md) collects the statistical and data qualifications.
