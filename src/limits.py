"""Simple market-risk limit monitoring helpers."""

from __future__ import annotations


def limit_status(value: float, limit: float) -> dict:
    """Calculate limit utilization and a simple status label."""
    if limit <= 0:
        raise ValueError("limit must be positive.")
    utilization = value / limit
    if utilization >= 1.0:
        status = "BREACH"
    elif utilization >= 0.90:
        status = "WATCH"
    else:
        status = "OK"
    return {
        "value": float(value),
        "limit": float(limit),
        "utilization": float(utilization),
        "status": status,
    }
