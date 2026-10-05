# Analysis Outputs

The outputs directory is reserved for generated analytical results. Generated CSV, SVG, JSON, and executive-summary files are intentionally ignored by Git so the repository does not present synthetic results as historical findings.

Run:

~~~bash
python run_analysis.py --mode live
~~~

to generate a historical public-proxy analysis, or:

~~~bash
python run_analysis.py --mode demo
~~~

to validate the pipeline with deterministic synthetic data.

The analysis produces portfolio positions, daily position P&L, VaR method comparison, component VaR, hypothetical and historical stress results, model-validation summaries, calibration sensitivity, limit monitoring, analysis metadata, charts, and an executive summary.

The executive summary includes the as-of date and explicitly identifies whether the analysis used public continuous futures proxies or synthetic demo data.
