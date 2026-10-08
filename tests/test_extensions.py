import unittest

import numpy as np
import pandas as pd

from src.continuous import build_continuous
from src.nonlinear import OptionLeg, full_revaluation_pnl


class ExtensionTests(unittest.TestCase):
    def panel(self):
        dates = pd.date_range("2024-01-01", periods=3)
        panel = pd.DataFrame(
            [
                (d, c, v)
                for d, vs in zip(dates, [(70, 75), (71, 76), (72, 77)])
                for c, v in zip(["A", "B"], vs)
            ],
            columns=["date", "contract", "settlement"],
        )
        return panel, pd.DataFrame({"date": dates, "contract": ["A", "B", "B"]})

    def test_roll_has_no_phantom_pnl(self):
        panel, schedule = self.panel()
        x = build_continuous(panel, schedule)
        np.testing.assert_allclose(x.raw_change.iloc[1:], [6, 1])
        np.testing.assert_allclose(x.adjusted_change.iloc[1:], [1, 1])
        self.assertEqual(x.adjusted.iloc[-1], 77)

    def test_missing_outgoing_rejected(self):
        p, s = self.panel()
        p = p.drop(p[(p.date == s.date.iloc[1]) & (p.contract == "A")].index)
        with self.assertRaises(ValueError):
            build_continuous(p, s)

    def test_negative_prices_and_no_future_pnl_leakage(self):
        p, s = self.panel()
        p["settlement"] -= 80
        full = build_continuous(p, s)
        short = build_continuous(p[p.date <= s.date.iloc[1]], s.iloc[:2])
        self.assertAlmostEqual(
            full.adjusted_change.iloc[1], short.adjusted_change.iloc[1]
        )

    def test_option_parity_and_expiry(self):
        # Long call - long put at expiry changes exactly like the future at r=0.
        legs = [
            OptionLeg("call", 70, 1000, 1 / 252, 0.4),
            OptionLeg("put", 70, -1000, 1 / 252, 0.4),
        ]
        pnl = full_revaluation_pnl(70, [-10, 0, 10], legs)
        np.testing.assert_allclose(pnl, [-10000, 0, 10000], atol=1e-9)
        with self.assertRaises(ValueError):
            full_revaluation_pnl(70, [-71], legs)
        with self.assertRaises(ValueError):
            full_revaluation_pnl(70, [1], legs, horizon_years=0.5)

    def test_refiner_hedge_offsets_321_physical_margin(self):
        from src.portfolio import load_positions_csv, pnl_history_from_prices

        positions = load_positions_csv("config/portfolio.csv")
        prices = pd.DataFrame({"CL=F": [70, 75], "RB=F": [2, 2.1], "HO=F": [2.2, 2.4]})
        hedge = pnl_history_from_prices(prices, positions).portfolio_pnl.iloc[0]
        physical = 20_000 * 42 * 0.1 + 10_000 * 42 * 0.2 - 30_000 * 5
        self.assertAlmostEqual(hedge + physical, 0)
