# Refiner margin and the hedge book

For 30,000 bbl crude, a stylized physical gross margin in USD is:

`20,000*42*RB + 10,000*42*HO - 30,000*CL`.

Its hedge is +30 CL contracts, -20 RB contracts and -10 HO contracts. CL is quoted USD/bbl with a 1,000-bbl multiplier; RB and HO are USD/gal with 42,000-gal multipliers. With perfectly matched references and quantities, the physical price-change margin plus hedge P&L cancels. A unit test verifies this identity independently.

The default report measures hedge-only mark-to-market, not total refinery cash flow. Product rallies can generate large short-product hedge losses while improving physical margins. Crude rallies with lagging products hurt physical margins and help this hedge. Configuration scenario names preserve that interpretation.

This is a crack benchmark, not a claim that any actual refinery makes exactly these yields. Processing costs, energy consumption, inventory timing, quality/location basis, production outages, contract rolls, hedge slippage and liquidity affect the real business. The NG position from the previous generic example has been removed; an NG energy-cost hedge would need its own consumption thesis.
