# Risk in a refiner’s 3-2-1 hedge book

How much can a refiner’s financial hedge lose in one day, and do the risk models recognize the same tail events?

The first point to get right is the book’s direction: a refiner buys crude and sells products, so the financial margin hedge is **long crude and short products**. A loss on that hedge can offset a gain in the physical margin. This engine reports the financial hedge book; it does not call a hedge loss a loss for the entire refinery.

## The book

| Position | Contracts | Physical units |
|---|---:|---:|
| WTI crude (CL) | +30 | +30,000 bbl |
| RBOB gasoline (RB) | -20 | -840,000 gal = -20,000 bbl |
| Heating oil / distillate proxy (HO) | -10 | -420,000 gal = -10,000 bbl |

That is the hedge of a stylized 30,000-barrel crude input yielding 20,000 barrels of gasoline and 10,000 barrels of distillate. It is a benchmark crack hedge, not a refinery process model. Yields, quality, location, timing and operating costs remain outside the book.

## Results you can inspect

The [sample workflow](https://github.com/akilatrades/energy-commodity-var-engine/actions/workflows/sample-run.yml) runs a dated public-data analysis, tests it and commits the result under `outputs/sample_run_2026-10/` when the download succeeds. It must fail rather than replace missing public data with synthetic prices. The price cutoff is October 7, 2026 (download end is exclusive).

Each completed sample includes the VaR/ES comparison, rolling backtest exception counts, stress results, charts, exact price inputs, configuration and input checksum. Check the sample’s metadata for its actual last observation. Results are point-in-time examples, not current risk limits or forecasts.

The offline option and roll examples are explicitly **synthetic fixtures**. Their numbers demonstrate calculations; they are not observed trading performance.

## Models

- Historical, Normal, Student-t Monte Carlo and exponentially weighted historical VaR/ES.
- Component VaR, hypothetical stress, worst historical fixed-book days and a configurable illustrative limit.
- Rolling forecasts made before each realized P&L, with exception counts and coverage/independence diagnostics.
- A contract-panel continuous-series builder that reconciles adjusted changes to the contract actually held.
- A separate full-revaluation WTI producer option case study using European Black-76 puts/calls, including collars and three-way collars.

[Refiner thesis and signs](docs/refiner_hedge.md) · [Contract rolls](docs/continuous_series.md) · [Option risk](docs/nonlinear_risk.md)

## Run it

```bash
pip install -r requirements.txt
pytest
python run_analysis.py --mode live --end 2026-10-08 --output-dir outputs/sample_run_2026-10
```

Offline smoke test:

```bash
python run_analysis.py --mode demo --output-dir outputs/demo
python run_option_risk.py
python run_roll_analysis.py --settlements examples/roll_fixture/settlements.csv --schedule examples/roll_fixture/schedule.csv --data-label "SYNTHETIC contract fixture" --output-dir outputs/roll_fixture
```

To replay a saved public price sample with the current configuration:

```bash
python run_analysis.py --mode snapshot --prices outputs/sample_run_2026-10/input_prices.csv --output-dir outputs/replay
```

For an exact replay, first use the configuration saved alongside that sample. The Monte Carlo seed is fixed. All risks use absolute price changes so negative underlying futures prices are not discarded from the linear model.

## What I learned / what I would do differently

Position signs and contract units matter before model selection. A 3-2-1 ratio in barrels has to be translated into 1,000-barrel crude contracts and 42,000-gallon product contracts. A risk number also needs a data-construction explanation: subtracting an unadjusted front-month series can turn a contract switch into fake P&L.

I would obtain dated settlement panels before claiming a historical improvement from roll adjustment. The code and reconciliation tests are implemented, but the committed roll example is synthetic. Yahoo’s continuous proxy cannot be reverse-engineered into exact contract history from prices alone. I would also add observed volatility surfaces and basis factors before combining the option example with a physical business exposure.

## Boundaries

The live book still uses Yahoo continuous proxies; the new roll adjustment has **not** been applied to them. The option module is a standalone WTI producer example, not part of the refiner’s default linear risk total. Its volatility is fixed unless explicitly stressed; it excludes volatility smile, American exercise, average-price settlement, liquidity, margin and counterparty risk. Black-76 rejects nonpositive forwards.

[Model limitations](docs/limitations.md) · [Validation](docs/model_validation.md). Public or synthetic portfolio research only; no employer or client data.
