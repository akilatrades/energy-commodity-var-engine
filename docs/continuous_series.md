# Continuous series with explicit rolls

`src/continuous.py` consumes a long panel (`date,contract,settlement`) and a predeclared selection schedule (`date,contract`). Every panel date must appear once in the schedule. Duplicate or missing required prices fail validation. The outgoing and incoming contracts both need a settlement on the roll date.

The convention is to hold yesterday’s selected contract through today’s settlement, mark its P&L, and then switch to the next contract at the same timestamp. On a roll day:

`roll gap = new contract settlement today - old contract settlement today`

`adjusted change = raw selected-price change - roll gap`.

The cumulative gap is subtracted from the raw chain and the whole history is shifted so its final level equals the final raw quote. Every adjusted difference must equal the held-contract price change. No roll jump becomes P&L. Cash margin, execution slippage and transaction fees are separate.

Back-adjusted *levels* can revise on future rolls and can be negative. Use their differences for dollar P&L, not percentage returns or historical absolute-price trading signals. The tests verify that adding future data does not change the previously calculated P&L.

`examples/roll_fixture/` has synthetic overlapping contracts and explicit switches; `outputs/roll_fixture/` compares raw versus adjusted P&L and VaR. The dated-contract audit below adds an observed long-dated price panel alongside that synthetic fixture.

Run the command in the main README with your own governed contract data and source label. Choose the schedule ex ante using actual expiry calendars and a documented liquidity/roll convention; do not select hindsight-optimal roll dates.

## What Yahoo actually returned

The dated-contract audit requested 48 CL/RB/HO tickers on October 8, 2026. Thirteen returned history; most expired 2025 contracts did not. The attempted 2025 front-month-style schedule therefore fails strict quote coverage for all three legs. The audit saves per-ticker availability, errors, exact vendor closes and environment. The observed prices are Yahoo **daily Close proxies**.

The currently listed November/December 2026 and January/February 2027 contracts do have overlapping historical observations. `run_real_contract_roll.py` applies the builder to those real prices, selecting November 2026 in 2025Q1, December 2026 in Q2, January 2027 in Q3 and February 2027 in Q4. This defines the quarterly **long-dated demonstration schedule**.

The available contracts have one inconsistent quote date, July 4, 2025. The saved audit exposes the incomplete date. The comparison uses common quote dates across all twelve contracts; endpoint differences retain the cumulative move across any missing date. The resulting sample has 251 quote dates and 250 P&L intervals.

| Same +30 CL / −20 RB / −10 HO financial book | Raw stitched changes | Held-contract adjusted changes |
|---|---:|---:|
| P&L standard deviation | $8,774 | $8,699 |
| Full-sample historical 99% VaR | $21,939 | $21,939 |
| Largest loss | $46,902 | $46,902 |
| Exceptions in 190 rolling 60-observation forecasts | 2 | 2 |

Roll adjustment removes non-economic jumps and reconciles every interval to the held contract, but the largest loss observations in this demonstration were not roll dates. The tail estimate and exception count therefore do not change. The rolling comparison uses a short 60-observation estimation window.

[Audit](../outputs/contract_audit_2026-10/metadata.json) · [Ticker availability](../outputs/contract_audit_2026-10/availability.csv) · [Actual roll-date P&L](../outputs/real_contract_roll_2026-10/roll_dates.csv) · [Comparison](../outputs/real_contract_roll_2026-10/comparison.csv)

```bash
# Reproduce from the committed real quote snapshot:
python run_real_contract_roll.py
# Optional new vendor retrieval (availability may change):
python probe_contract_data.py
```

The front-month repair still needs expired-contract history and an explicit roll policy. See the [April 2020 diagnosis](backtest_diagnosis.md#april-20-2020-the-exception-to-explain-first) and consolidated [limitations](limitations.md).
