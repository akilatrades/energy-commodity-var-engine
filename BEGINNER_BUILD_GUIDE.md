# Beginner Build Guide — Energy Commodity VaR Engine

This file is for learning the project, not impressing a recruiter. Follow it in order.

## Step 1 — Understand the business problem before the math

Imagine a trading desk owns several energy futures positions.

Every day, market prices move. Those price moves create profit or loss.

Market Risk wants to know:

```text
What can the book lose?
What is creating that risk?
Does the model make sense?
What happens if markets move sharply?
Are we inside our limits?
```

That is the entire project.

## Step 2 — Understand the portfolio

The default book contains WTI crude, RBOB gasoline, heating oil, and natural gas futures.

A positive number of contracts means **long**. A negative number means **short**.

Start with `src/portfolio.py`.

Do not move on until you can explain this formula:

```text
Daily futures P&L
= contracts × contract multiplier × price change
```

Example:

```text
2 CL contracts long
CL multiplier = 1,000 barrels
Price rises $1/bbl

P&L = 2 × 1,000 × $1 = +$2,000
```

If price instead falls $2:

```text
P&L = 2 × 1,000 × -$2 = -$4,000
```

That exact example is tested in `tests/test_portfolio.py`.

## Step 3 — Understand portfolio P&L

Each position gets its own daily P&L series.

Then:

```text
Portfolio P&L
= WTI P&L
+ RBOB P&L
+ Heating Oil P&L
+ Natural Gas P&L
```

Some positions can lose money while others make money. That is where correlation and diversification become important.

Open `notebooks/01_portfolio_and_pnl.ipynb`.

## Step 4 — Learn Historical VaR first

Forget the other methods until Historical VaR makes sense.

Suppose you have 1,000 daily P&L observations.

A 99% Historical VaR looks at the very bad end of that history and asks approximately:

> What loss threshold was only exceeded about 1% of the time?

If 99% VaR is $400,000, do **not** say:

> We cannot lose more than $400,000.

Say:

> Under this historical sample and method, $400,000 is the 99% one-day loss threshold. Losses can be worse.

The function is `historical_var()` in `src/var_models.py`.

## Step 5 — Learn Expected Shortfall

VaR gives the edge of the tail.

Expected Shortfall asks:

> Once we are already in that bad tail, what is the average loss?

If:

```text
99% VaR = $400,000
99% ES  = $560,000
```

then $400k is the threshold and $560k describes average severity beyond that threshold.

## Step 6 — Learn Parametric VaR

Parametric VaR simplifies the P&L distribution by estimating a mean and standard deviation and assuming a normal shape.

That makes it fast and easy to calculate.

The trade-off is that real markets can have fat tails, changing volatility, and extreme events that do not behave normally.

Your interview explanation should be:

> Parametric VaR is transparent and efficient, but its distribution assumptions can miss tail behavior, so I compare it with historical methods, stress testing, and backtesting.

## Step 7 — Learn Monte Carlo VaR

Monte Carlo means simulation.

The current project:

1. estimates the historical P&L mean and volatility;
2. simulates many possible P&L observations;
3. calculates VaR from the simulated distribution.

This is a **baseline Monte Carlo**, not a production bank model.

A more advanced version could simulate individual market risk factors, stochastic volatility, options, curves, and nonlinear pricing.

## Step 8 — Understand weighted Historical VaR

Ordinary Historical VaR treats an observation from years ago the same as yesterday.

Weighted Historical VaR asks whether recent conditions should matter more.

The project uses exponential weights so recent observations receive more probability mass.

Important: this does not automatically make the model "better." The decay rate is itself a model assumption that must be validated.

## Step 9 — Understand risk attribution

Imagine total VaR is $500,000.

Management will naturally ask:

> What is creating the $500,000?

Component VaR allocates the normal-theory portfolio VaR across positions.

If a component is positive, that position contributes to risk.

If it is negative, the position is offsetting other positions under the current covariance relationship.

Open `src/attribution.py` and `notebooks/04_stress_attribution_and_limits.ipynb`.

## Step 10 — Understand stress testing

VaR asks a percentile question.

Stress testing asks a scenario question.

Examples:

```text
What if crude falls 20%?
What if products rally while crude barely moves?
What if natural gas jumps 35%?
```

Neither tool replaces the other.

VaR helps with recurring statistical risk measurement. Stress tests help examine specific severe or dislocated markets.

## Step 11 — Understand backtesting

This is one of the most important sections for a Market Risk interview.

For each day, the project does:

```text
previous 250 days
    -> calculate VaR
    -> move forward one day
    -> compare VaR with actual P&L
```

If actual P&L is worse than `-VaR`, that is a **VaR exception**.

At 99% confidence, the model expects exceptions to be rare, but not zero.

## Step 12 — Kupiec test in plain English

The Kupiec test asks:

> Did I get roughly the right number of exceptions?

Example:

A 99% model tested for 500 days theoretically expects around five exceptions on average.

If you get 40 exceptions, something is clearly suspicious.

If you get zero, that can also mean the model is excessively conservative.

The test converts that idea into a formal likelihood-ratio test.

You do not need to memorize the likelihood formula yet.

## Step 13 — Christoffersen test in plain English

Suppose you get five exceptions across 500 days.

That number may look reasonable.

But what if all five happen in the same week?

That suggests the model may fail when volatility rises.

Christoffersen's independence test asks whether exceptions look randomly spaced or clustered.

So remember:

```text
Kupiec -> right number of exceptions?
Christoffersen -> are exceptions independent, or clustered?
```

## Step 14 — Understand limits

Market Risk does not only calculate risk.

It monitors risk against approved boundaries.

Example:

```text
Current 99% VaR = $450,000
Approved VaR limit = $500,000

Utilization = 450 / 500 = 90%
```

That is high utilization.

The project uses simple example statuses:

```text
< 90%       -> OK
90% to 100% -> WATCH
>= 100%     -> BREACH
```

These are project conventions, not universal bank policy.

## Step 15 — Know what the project does NOT do

This is just as important as knowing what it does.

Do not pretend this is a bank production risk platform.

It currently does not fully model:

- options Greeks,
- nonlinear pricing,
- swaps and structured products,
- intraday changes,
- liquidity add-ons,
- official independent market data,
- exact futures contract rolls,
- P&L explain,
- credit risk,
- production trading-system controls.

A strong interview answer acknowledges those gaps.

## Step 16 — The 30-second explanation you are working toward

> I built a Python market-risk framework around an illustrative energy futures portfolio. I first convert WTI, gasoline, heating-oil, and natural-gas positions into daily position and portfolio P&L. I then compare Historical, Parametric, Monte Carlo, and weighted Historical VaR, calculate Expected Shortfall, attribute parametric VaR by position, and run deterministic stress tests. I also perform rolling out-of-sample VaR backtesting using Kupiec coverage and Christoffersen independence tests, then compare the current risk number with an illustrative limit. The main objective is not just calculating VaR; it is understanding what drives the risk, whether the model behaves reasonably, and how the result would be communicated and controlled.

Do not memorize this immediately. Build your understanding until you can say the same thing in your own words.

## Step 17 — Learning order

Use this exact order:

1. `docs/glossary.md`
2. `notebooks/01_portfolio_and_pnl.ipynb`
3. `src/portfolio.py`
4. `notebooks/02_var_methods.ipynb`
5. `docs/var_models.md`
6. `src/var_models.py`
7. `docs/attribution.md`
8. `docs/stress_testing.md`
9. `notebooks/04_stress_attribution_and_limits.ipynb`
10. `docs/backtesting.md`
11. `notebooks/03_backtesting.ipynb`
12. `src/backtesting.py`
13. `docs/limits.md`
14. `docs/limitations.md`
15. `run_analysis.py`

Only read `run_analysis.py` after the individual ideas make sense.

## Step 18 — Resume honesty

Until the project has actually been run and reviewed, do not put specific findings on the resume such as:

- "found losses clustered during volatile periods"
- "corrected the model"
- a specific backtest p-value
- a specific VaR reduction

Those statements need actual evidence from the finished analysis.

A safe project description during development is:

> **Energy Commodity Portfolio VaR & Market Risk Analytics (Python)** — Building a multi-commodity energy risk framework comparing Historical, Parametric, Monte Carlo, and weighted Historical VaR; adding Expected Shortfall, component risk attribution, deterministic stress testing, rolling VaR backtesting, and illustrative risk-limit monitoring.

Once the project is completed using the chosen historical data and you understand the results, update the resume with real findings only.
