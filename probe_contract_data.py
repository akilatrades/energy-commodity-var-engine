"""Audit Yahoo dated-contract closes; never substitute continuous proxies."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from src.continuous import build_continuous

MONTH_CODES = "FGHJKMNQUVXZ"


def ticker(root, delivery):
    return f"{root}{MONTH_CODES[delivery.month - 1]}{delivery.year % 100:02d}.NYM"


def main():
    out = Path("outputs/contract_audit_2026-10")
    out.mkdir(parents=True, exist_ok=True)
    audit, panels = [], []
    for root in ["CL", "RB", "HO"]:
        deliveries = list(pd.date_range("2025-03-01", "2026-02-01", freq="MS"))
        deliveries += list(pd.date_range("2026-11-01", "2027-02-01", freq="MS"))
        for delivery in deliveries:
            symbol = ticker(root, delivery)
            try:
                data = yf.Ticker(symbol).history(
                    start="2024-12-01", end="2026-10-08", auto_adjust=False,
                    actions=False, raise_errors=True
                )
                close = data["Close"].dropna()
                close.index = pd.to_datetime(close.index.date)
                if not np.isfinite(close).all():
                    raise ValueError("Nonfinite quote")
                audit.append(dict(root=root, ticker=symbol, observations=len(close),
                                  first=str(close.index.min().date()) if len(close) else "",
                                  last=str(close.index.max().date()) if len(close) else "",
                                  error="" if len(close) else "No closes returned"))
                panels.extend(dict(date=date, root=root, contract=symbol, settlement=float(value))
                              for date, value in close.items())
            except Exception as exc:
                audit.append(dict(root=root, ticker=symbol, observations=0,
                                  first="", last="", error=f"{type(exc).__name__}: {exc}"[:400]))
    pd.DataFrame(audit).to_csv(out / "availability.csv", index=False)
    panel = pd.DataFrame(panels, columns=["date", "root", "contract", "settlement"])
    panel.to_csv(out / "vendor_closes.csv.gz", index=False,
                 compression={"method": "gzip", "mtime": 0})
    report = []
    for root in ["CL", "RB", "HO"]:
        p = panel[(panel.root == root) & (panel.date >= pd.Timestamp("2025-01-01"))
                  & (panel.date < pd.Timestamp("2026-01-01"))].copy()
        dates = sorted(p.date.unique())
        schedule = pd.DataFrame([dict(date=d, contract=ticker(root, pd.Timestamp(d) + pd.offsets.MonthBegin(2)))
                                 for d in dates])
        # A full calendar-year claim needs both boundary months and a normal
        # number of trading observations, then the builder requires every held
        # and outgoing quote. Missing data are not filled or quietly dropped.
        try:
            if len(dates) < 240 or pd.Timestamp(dates[0]).month != 1 or pd.Timestamp(dates[-1]).month != 12:
                raise ValueError(f"Insufficient year coverage: {len(dates)} dates")
            series = build_continuous(p[["date", "contract", "settlement"]], schedule)
            series.to_csv(out / f"{root}_continuous.csv")
            report.append(dict(root=root, status="built", dates=len(series),
                               roll_dates=int((series.roll_gap != 0).sum())))
        except ValueError as exc:
            report.append(dict(root=root, status="unavailable", reason=str(exc)))
    # A matched financial book is reported only when every leg has a real panel.
    if all(row["status"] == "built" for row in report):
        books = {}
        for kind in ["raw_change", "adjusted_change"]:
            legs = [pd.read_csv(out / f"{root}_continuous.csv", index_col="date", parse_dates=True)[kind] * size
                    for root, size in [("CL", 30000), ("RB", -840000), ("HO", -420000)]]
            books[kind] = pd.concat(legs, axis=1).dropna().sum(axis=1)
        matched = pd.concat(books, axis=1).dropna()
        matched.to_csv(out / "matched_book_pnl.csv")
        pd.DataFrame([dict(series=k, days=len(matched), historical_var_99=-matched[k].quantile(.01),
                           worst_loss=-matched[k].min(), pnl_std=matched[k].std()) for k in books]).to_csv(
                               out / "matched_book_comparison.csv", index=False)
    metadata = dict(as_of="2026-10-08", vendor="Yahoo Finance via yfinance",
                    price_type="Vendor daily Close, NOT verified exchange settlement",
                    attempted_year="2025", schedule="Hold delivery month two months ahead; switch at first observed date of month",
                    root_results=report, available_tickers=sum(x["observations"] > 0 for x in audit),
                    attempted_tickers=len(audit), raw_sha256=hashlib.sha256((out / "vendor_closes.csv.gz").read_bytes()).hexdigest(),
                    warning="Ticker existence does not establish usable historical coverage; no synthetic fallback.")
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
