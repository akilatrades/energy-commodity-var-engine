import numpy as np
import pandas as pd
import pytest
from model import (
    contract_roll_days,
    crack_321,
    distillate_crack,
    gasoline_crack,
    mean_reversion_position,
    next_day_pnl,
    zscore,
)


def test_hand_computed_cracks():
    # CL $70/bbl, RBOB $2.50/gal, HO $3.00/gal
    assert gasoline_crack(70, 2.50) == pytest.approx(35.0)
    assert distillate_crack(70, 3.00) == pytest.approx(56.0)
    # (2 x 105 + 126 - 210) / 3 = 42
    assert crack_321(70, 2.50, 3.00) == pytest.approx(42.0)


def test_321_is_weighted_average_of_single_cracks():
    cl, rb, ho = 81.3, 2.41, 2.87
    blend = (2 * gasoline_crack(cl, rb) + distillate_crack(cl, ho)) / 3
    assert crack_321(cl, rb, ho) == pytest.approx(blend)


def test_signal_has_no_look_ahead():
    rng = np.random.default_rng(0)
    index = pd.bdate_range("2020-01-01", periods=200)
    crack = pd.Series(20 + rng.normal(0, 1, 200).cumsum(), index=index)
    base = mean_reversion_position(zscore(crack))
    changed = crack.copy()
    changed.iloc[150:] += 50  # rewrite the future
    after = mean_reversion_position(zscore(changed))
    pd.testing.assert_series_equal(base.iloc[:150], after.iloc[:150])


def test_pnl_uses_next_day_change():
    index = pd.bdate_range("2021-03-01", periods=4)
    crack = pd.Series([10.0, 12.0, 11.0, 15.0], index=index)
    position = pd.Series([1, -1, 1, 0], index=index)
    frame = next_day_pnl(crack, position)
    assert frame.pnl.tolist() == [2.0, 1.0, 4.0]


def test_roll_day_changes_are_dropped():
    index = pd.bdate_range("2021-03-29", periods=4)  # Mar 29, 30, 31, Apr 1
    crack = pd.Series([10.0, 11.0, 12.0, 30.0], index=index)
    position = pd.Series([1, 1, 1, 0], index=index)
    rolls = contract_roll_days(index)
    assert rolls.tolist() == [True, False, False, True]
    frame = next_day_pnl(crack, position, rolls)
    assert frame.index.max() == pd.Timestamp("2021-03-30")  # Mar 31 -> Apr 1 dropped
