import unittest

import numpy as np
import pandas as pd

from src.filtered_historical import ewma_prior_volatility, filtered_forecasts, month_turn_flags


class FilterTests(unittest.TestCase):
    def sample(self):
        return pd.Series(np.random.default_rng(2).normal(size=600), index=pd.bdate_range("2020-01-01", periods=600))

    def test_future_losses_cannot_change_forecast(self):
        x = self.sample()
        before = filtered_forecasts(x)
        changed = x.copy()
        changed.iloc[500:] *= 100
        after = filtered_forecasts(changed)
        np.testing.assert_allclose(before["var"].iloc[:191], after["var"].iloc[:191])
        self.assertNotEqual(before["var"].iloc[192], after["var"].iloc[192])

    def test_ewma_timing_and_scaling(self):
        x = self.sample()
        s = ewma_prior_volatility(x)
        self.assertAlmostEqual(s.iloc[60]**2, np.square(x.iloc[:60]).mean())
        self.assertAlmostEqual(s.iloc[61]**2, .94*s.iloc[60]**2+.06*x.iloc[60]**2)
        a = filtered_forecasts(x)
        b = filtered_forecasts(10*x)
        np.testing.assert_allclose(10*a["var"], b["var"])

    def test_flags_do_not_remove_realized_losses_or_use_sample_end(self):
        x = self.sample()
        a = filtered_forecasts(x)
        b = filtered_forecasts(x, exclude_training_flags=month_turn_flags(x.index))
        np.testing.assert_allclose(a.realized_pnl, b.realized_pnl)
        self.assertEqual(len(a), len(b))
        flags = month_turn_flags(pd.DatetimeIndex(["2026-10-07", "2026-10-30"]))
        self.assertEqual(flags.tolist(), [False, True])

    def test_invalid_data_fails(self):
        x = self.sample()
        x.iloc[100] = np.nan
        with self.assertRaises(ValueError):
            filtered_forecasts(x)
