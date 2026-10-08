# Continuous series with explicit rolls

`src/continuous.py` consumes a long panel (`date,contract,settlement`) and a predeclared selection schedule (`date,contract`). Every panel date must appear once in the schedule. Duplicate or missing required prices fail validation. The outgoing and incoming contracts both need a settlement on the roll date.

The convention is to hold yesterday’s selected contract through today’s settlement, mark its P&L, and then switch to the next contract at the same timestamp. On a roll day:

`roll gap = new contract settlement today - old contract settlement today`

`adjusted change = raw selected-price change - roll gap`.

The cumulative gap is subtracted from the raw chain and the whole history is shifted so its final level equals the final raw quote. Every adjusted difference must equal the held-contract price change. No roll jump becomes P&L. Cash margin, execution slippage and transaction fees are separate.

Back-adjusted *levels* can revise on future rolls and can be negative. Use their differences for dollar P&L, not percentage returns or historical absolute-price trading signals. The tests verify that adding future data does not change the previously calculated P&L.

`examples/roll_fixture/` has synthetic overlapping contracts and explicit switches; `outputs/roll_fixture/` compares raw versus adjusted P&L and VaR. This is a controlled demonstration, not observed empirical evidence. A real dated CL/RB/HO panel remains necessary. The generic Yahoo proxy and EIA monthly C1–C4 averages lack enough information to reconstruct it.

Run the command in the main README with your own governed contract data and source label. Choose the schedule ex ante using actual expiry calendars and a documented liquidity/roll convention; do not select hindsight-optimal roll dates.
