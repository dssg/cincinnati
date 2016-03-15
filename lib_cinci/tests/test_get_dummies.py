import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np
from nose.tools import raises

from lib_cinci.util import get_dummies



@raises(ValueError)
def test_illegal_value():
    possible_values = ["val1", "val2", "val3"]
    data = pd.Series(["val1", "val3", "val1", "val4"])

    get_dummies(data, possible_values)


def test_empty_input():
    possible_values = ["val1", "val2", "val3"]
    data = pd.Series([])
    expected = pd.DataFrame([], columns=possible_values)

    actual = get_dummies(data, possible_values)
    assert_frame_equal(expected, actual)


def test_only_one_value():
    possible_values = ["val1", "val2", "val3"]
    data = pd.Series(["val2"])
    expected = pd.DataFrame([(0, 1, 0)], columns=possible_values)

    actual = get_dummies(data, possible_values)
    assert_frame_equal(expected, actual)


def test_only_one_value_many_times():
    possible_values = ["val1", "val2", "val3"]
    data = pd.Series(["val2", "val2", "val2", "val2", "val2", "val2"])
    expected = pd.DataFrame([(0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)], columns=possible_values)

    actual = get_dummies(data, possible_values)
    assert_frame_equal(expected, actual)

def test_all_values():
    possible_values = ["val1", "val2", "val3"]
    data = pd.Series(["val1", "val3", "val1", "val2"])
    expected = pd.DataFrame([(1, 0, 0), (0, 0, 1), (1, 0, 0), (0, 1, 0)], columns=possible_values)

    actual = get_dummies(data, possible_values)
    assert_frame_equal(expected, actual)


def test_all_values_and_nan():
    possible_values = ["val1", "val2", "val3"]
    data = pd.Series(["val1", "val3", "val1", "val2", np.nan])
    expected = pd.DataFrame([(1, 0, 0), (0, 0, 1), (1, 0, 0), (0, 1, 0), (np.nan, np.nan, np.nan)],
                             columns=possible_values)

    actual = get_dummies(data, possible_values)
    assert_frame_equal(expected, actual)


def test_only_nan():
    possible_values = ["val1", "val2", "val3"]
    data = pd.Series([np.nan, np.nan, np.nan, np.nan])
    expected = pd.DataFrame([(np.nan, np.nan, np.nan), (np.nan, np.nan, np.nan), (np.nan, np.nan, np.nan),
                             (np.nan, np.nan, np.nan)], columns=possible_values)

    actual = get_dummies(data, possible_values)
    assert_frame_equal(expected, actual)