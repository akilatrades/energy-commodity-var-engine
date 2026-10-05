# Risk Limits

The project compares current Historical VaR with a configurable illustrative limit stored in **config/risk_limits.json**.

Reported fields are current VaR, limit, utilization, and status.

The default project convention is:

- utilization below 90%: OK
- 90% to below 100%: WATCH
- 100% or above: BREACH

These thresholds are project assumptions, not universal industry rules.

In a production environment, escalation and remediation would be governed by formal policy and could include trader notification, desk escalation, risk reduction, temporary limit approval, or documented exception handling.
