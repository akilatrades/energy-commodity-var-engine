"""VaR forecast backtesting utilities."""

from __future__ import annotations

import math

import pandas as pd
from scipy.stats import chi2

from src.var_models import historical_var, parametric_var, weighted_historical_var


def rolling_var_forecasts(
    pnl: pd.Series,
    window: int = 250,
    confidence: float = 0.99,
    method: str = "historical",
    decay: float = 0.97,
) -> pd.DataFrame:
    """Estimate VaR using only prior observations and test the next day's P&L."""
    x = pd.Series(pnl, copy=True).dropna().astype(float).sort_index()
    if len(x) <= window:
        raise ValueError("Not enough observations for rolling backtesting.")

    rows = []
    for i in range(window, len(x)):
        train = x.iloc[i - window : i]
        realized = float(x.iloc[i])

        if method == "historical":
            var = historical_var(train, confidence)
        elif method == "parametric":
            var = parametric_var(train, confidence)
        elif method == "weighted_historical":
            var = weighted_historical_var(train, confidence, decay)
        else:
            raise ValueError("method must be historical, parametric, or weighted_historical.")

        rows.append(
            {
                "date": x.index[i],
                "realized_pnl": realized,
                "var": var,
                "exception": realized < -var,
            }
        )

    return pd.DataFrame(rows).set_index("date")


def kupiec_pof_test(exceptions: pd.Series, confidence: float = 0.99) -> dict:
    """Kupiec unconditional-coverage likelihood-ratio test."""
    e = pd.Series(exceptions).astype(bool).dropna()
    n = int(len(e))
    x = int(e.sum())
    if n == 0:
        raise ValueError("No exception observations supplied.")

    p = 1 - confidence
    phat = x / n

    def safe_term(prob: float, count: int) -> float:
        if count == 0:
            return 0.0
        if prob <= 0:
            return -math.inf
        return count * math.log(prob)

    ll_null = safe_term(1 - p, n - x) + safe_term(p, x)
    ll_alt = safe_term(1 - phat, n - x) + safe_term(phat, x)
    if not math.isfinite(ll_alt):
        lr = math.inf
        p_value = 0.0
    else:
        lr = max(-2 * (ll_null - ll_alt), 0.0)
        p_value = float(1 - chi2.cdf(lr, df=1))

    return {
        "observations": n,
        "exceptions": x,
        "expected_exception_rate": p,
        "actual_exception_rate": phat,
        "lr_pof": float(lr),
        "p_value": p_value,
    }


def christoffersen_independence_test(exceptions: pd.Series) -> dict:
    """Christoffersen first-order exception-independence test."""
    e = pd.Series(exceptions).astype(int).dropna().to_numpy()
    if len(e) < 2:
        raise ValueError("At least two exception observations are required.")

    n00 = n01 = n10 = n11 = 0
    for prev, curr in zip(e[:-1], e[1:]):
        if prev == 0 and curr == 0:
            n00 += 1
        elif prev == 0 and curr == 1:
            n01 += 1
        elif prev == 1 and curr == 0:
            n10 += 1
        else:
            n11 += 1

    def ratio(a: int, b: int) -> float:
        return a / (a + b) if (a + b) else 0.0

    pi01 = ratio(n01, n00)
    pi11 = ratio(n11, n10)
    total_exc = n01 + n11
    total_trans = n00 + n01 + n10 + n11
    pi = total_exc / total_trans if total_trans else 0.0

    def loglik(prob: float, successes: int, failures: int) -> float:
        out = 0.0
        if successes:
            if prob <= 0:
                return -math.inf
            out += successes * math.log(prob)
        if failures:
            if prob >= 1:
                return -math.inf
            out += failures * math.log(1 - prob)
        return out

    ll_null = loglik(pi, total_exc, total_trans - total_exc)
    ll_alt = loglik(pi01, n01, n00) + loglik(pi11, n11, n10)

    if not math.isfinite(ll_alt):
        lr = math.inf
        p_value = 0.0
    else:
        lr = max(-2 * (ll_null - ll_alt), 0.0)
        p_value = float(1 - chi2.cdf(lr, df=1))

    return {
        "n00": n00,
        "n01": n01,
        "n10": n10,
        "n11": n11,
        "lr_independence": float(lr),
        "p_value": p_value,
    }


def summarize_backtest(
    results: pd.DataFrame,
    confidence: float = 0.99,
) -> pd.DataFrame:
    """Return coverage and independence diagnostics in one table."""
    kupiec = kupiec_pof_test(results["exception"], confidence)
    christ = christoffersen_independence_test(results["exception"])
    row = {
        "confidence": confidence,
        "observations": kupiec["observations"],
        "exceptions": kupiec["exceptions"],
        "expected_exception_rate": kupiec["expected_exception_rate"],
        "actual_exception_rate": kupiec["actual_exception_rate"],
        "lr_pof": kupiec["lr_pof"],
        "kupiec_p_value": kupiec["p_value"],
        "n00": christ["n00"],
        "n01": christ["n01"],
        "n10": christ["n10"],
        "n11": christ["n11"],
        "lr_independence": christ["lr_independence"],
        "independence_p_value": christ["p_value"],
        "kupiec_pass_5pct": kupiec["p_value"] >= 0.05,
        "independence_pass_5pct": christ["p_value"] >= 0.05,
    }
    return pd.DataFrame([row])
