"""Rolling VaR backtesting and calibration sensitivity."""

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
    mean_adjusted: bool = False,
) -> pd.DataFrame:
    """Estimate VaR from prior observations and compare with next realized P&L."""
    x = pd.Series(pnl, copy=True).dropna().astype(float).sort_index()
    if len(x) <= window:
        raise ValueError("Not enough observations for rolling backtesting.")

    rows: list[dict] = []
    for i in range(window, len(x)):
        train = x.iloc[i - window : i]
        realized = float(x.iloc[i])

        if method == "historical":
            var = historical_var(train, confidence)
        elif method == "parametric":
            var = parametric_var(train, confidence, mean_adjusted)
        elif method == "weighted_historical":
            var = weighted_historical_var(train, confidence, decay)
        else:
            raise ValueError(
                "method must be historical, parametric, or weighted_historical."
            )

        rows.append(
            {
                "date": x.index[i],
                "method": method,
                "window": window,
                "decay": decay if method == "weighted_historical" else None,
                "realized_pnl": realized,
                "var": var,
                "exception": realized < -var,
            }
        )

    return pd.DataFrame(rows).set_index("date")


def kupiec_pof_test(exceptions: pd.Series, confidence: float = 0.99) -> dict:
    e = pd.Series(exceptions).astype(bool).dropna()
    n = int(len(e))
    x = int(e.sum())
    if n == 0:
        raise ValueError("No exception observations supplied.")

    p = 1 - confidence
    phat = x / n

    def term(prob: float, count: int) -> float:
        if count == 0:
            return 0.0
        if prob <= 0:
            return -math.inf
        return count * math.log(prob)

    ll_null = term(1 - p, n - x) + term(p, x)
    ll_alt = term(1 - phat, n - x) + term(phat, x)

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

    def probability(successes: int, failures: int) -> float:
        total = successes + failures
        return successes / total if total else 0.0

    pi01 = probability(n01, n00)
    pi11 = probability(n11, n10)
    total_exc = n01 + n11
    total_transitions = n00 + n01 + n10 + n11
    pi = total_exc / total_transitions if total_transitions else 0.0

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

    ll_null = loglik(pi, total_exc, total_transitions - total_exc)
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
    kupiec = kupiec_pof_test(results["exception"], confidence)
    christ = christoffersen_independence_test(results["exception"])
    conditional_lr = kupiec["lr_pof"] + christ["lr_independence"]
    conditional_p = (
        0.0
        if math.isinf(conditional_lr)
        else float(1 - chi2.cdf(conditional_lr, df=2))
    )

    row = {
        "method": str(results["method"].iloc[0]),
        "window": int(results["window"].iloc[0]),
        "decay": results["decay"].iloc[0],
        "confidence": confidence,
        "observations": kupiec["observations"],
        "exceptions": kupiec["exceptions"],
        "expected_exception_rate": kupiec["expected_exception_rate"],
        "actual_exception_rate": kupiec["actual_exception_rate"],
        "lr_pof": kupiec["lr_pof"],
        "kupiec_p_value": kupiec["p_value"],
        "lr_independence": christ["lr_independence"],
        "independence_p_value": christ["p_value"],
        "conditional_coverage_lr": conditional_lr,
        "conditional_coverage_p_value": conditional_p,
        "kupiec_pass_5pct": kupiec["p_value"] >= 0.05,
        "independence_pass_5pct": christ["p_value"] >= 0.05,
        "conditional_coverage_pass_5pct": conditional_p >= 0.05,
    }
    return pd.DataFrame([row])


def compare_backtests(
    pnl: pd.Series,
    methods: list[str],
    window: int,
    confidence: float,
    decay: float,
    mean_adjusted: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summaries = []
    forecasts = []

    for method in methods:
        result = rolling_var_forecasts(
            pnl,
            window=window,
            confidence=confidence,
            method=method,
            decay=decay,
            mean_adjusted=mean_adjusted,
        )
        summaries.append(summarize_backtest(result, confidence))
        forecasts.append(result.reset_index())

    return (
        pd.concat(summaries, ignore_index=True),
        pd.concat(forecasts, ignore_index=True),
    )


def calibration_sensitivity(
    pnl: pd.Series,
    windows: list[int],
    confidence: float,
    decays: list[float],
    mean_adjusted: bool = False,
) -> pd.DataFrame:
    """Report validation sensitivity without selecting a preferred model."""
    summaries = []

    for window in windows:
        if len(pnl.dropna()) <= window:
            continue

        for method in ["historical", "parametric"]:
            result = rolling_var_forecasts(
                pnl,
                window=window,
                confidence=confidence,
                method=method,
                mean_adjusted=mean_adjusted,
            )
            summaries.append(summarize_backtest(result, confidence))

        for decay in decays:
            result = rolling_var_forecasts(
                pnl,
                window=window,
                confidence=confidence,
                method="weighted_historical",
                decay=decay,
                mean_adjusted=mean_adjusted,
            )
            summaries.append(summarize_backtest(result, confidence))

    if not summaries:
        raise ValueError("No sensitivity specification had enough observations.")
    return pd.concat(summaries, ignore_index=True)
