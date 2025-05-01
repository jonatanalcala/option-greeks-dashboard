import numpy as np
import pandas as pd
import pytest

from option_greeks_dashboard.utils.helpers import simulate_gbm, simulate_ou, simulate_vg

def test_simulate_gbm_shape_and_reproducibility():
    df1 = simulate_gbm(100, 0.05, 0.2, 1.0, 10, 3, seed=42)
    df2 = simulate_gbm(100, 0.05, 0.2, 1.0, 10, 3, seed=42)
    assert df1.shape == (11, 3)
    pd.testing.assert_frame_equal(df1, df2)

def test_simulate_ou_shape():
    df = simulate_ou(0, 1.0, 0.0, 0.3, 1.0, 10, 2, seed=0)
    assert df.shape == (11, 2)

def test_simulate_vg_nonnegative():
    df = simulate_vg(100, 0.1, 0.2, 0.2, 1.0, 10, 4, seed=0)
    assert (df.values >= 0).all()
