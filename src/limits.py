"""Market-risk limit monitoring."""

from __future__ import annotations

import json
from pathlib import Path


def load_risk_limits(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    if "var_99_1d_usd" not in config:
        raise ValueError("Risk-limit configuration is missing var_99_1d_usd.")
    return config


def limit_status(
    value: float,
    limit: float,
    watch_threshold: float = 0.90,
) -> dict:
    if limit <= 0:
        raise ValueError("limit must be positive.")
    if not 0 < watch_threshold < 1:
        raise ValueError("watch_threshold must be between 0 and 1.")

    utilization = value / limit
    if utilization >= 1.0:
        status = "BREACH"
    elif utilization >= watch_threshold:
        status = "WATCH"
    else:
        status = "OK"

    return {
        "value": float(value),
        "limit": float(limit),
        "utilization": float(utilization),
        "status": status,
    }
