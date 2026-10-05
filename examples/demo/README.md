# Demo Mode

Demo mode exists only to make the full pipeline reproducible without external market-data access.

The generated price paths are deterministic synthetic data with correlated energy-market behavior and time-varying volatility.

Use:

~~~bash
python run_analysis.py --mode demo --output-dir /tmp/energy-var-demo
~~~

Synthetic results should not be cited as historical findings, used as resume performance claims, or compared with real trading-book risk.
