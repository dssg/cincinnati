"""
Tests for feature loading and making train/test datasets
"""

import unittest
import pandas as pd
import numpy as np
from nose.tools import raises

from test_utils import FeatureDatabase, iso_date, date, assert_frame_equal
from lib_cinci import dataset, util


# class TestLabels(unittest.TestCase):

#     def setUp(self):
#         self.db = FeatureDatabase()

#     def tearDown(self):
#         self.db.close()

#     def test_single_label_in_timerange(self):
#         labels = [{"parcel_id": "abc", "inspection_date": iso_date("01Mar2004"), "viol_outcome": 0}]
#         start_date, end_date = iso_date("01Mar2003"), iso_date("01Mar2006")

#         expected = labels
#         expected = pd.DataFrame(expected).set_index(["parcel_id", "inspection_date"])

#         self.db.add_labels(labels)
#         actual = dataset.load_labels(start_date, end_date)
#         assert_frame_equal(expected, actual)

#     def test_single_label_not_in_timerange(self):
#         labels = [{"parcel_id": "abc", "inspection_date": iso_date("01Mar2004"), "viol_outcome": 0}]
#         start_date, end_date = iso_date("01Mar2005"), iso_date("01Mar2006")

#         expected = []
#         expected = pd.DataFrame(expected, columns=["parcel_id", "inspection_date", "viol_outcome"]).set_index(["parcel_id", "inspection_date"])

#         self.db.add_labels(labels)
#         actual = dataset.load_labels(start_date, end_date)
#         assert_frame_equal(expected, actual)

#     def test_two_labels_in_timerange(self):
#         labels = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "viol_outcome": 0},
#                   {"parcel_id": "abc", "inspection_date": iso_date("15Apr2004"), "viol_outcome": 1}]
#         start_date, end_date = iso_date("01Mar2003"), iso_date("01Mar2006")

#         expected = labels
#         expected = pd.DataFrame(expected).set_index(["parcel_id", "inspection_date"])

#         self.db.add_labels(labels)
#         actual = dataset.load_labels(start_date, end_date)
#         assert_frame_equal(expected, actual)

#     def test_two_labels_one_in_timerange(self):
#         labels = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "viol_outcome": 0},
#                   {"parcel_id": "abc", "inspection_date": iso_date("15Apr2004"), "viol_outcome": 1}]
#         start_date, end_date = iso_date("01Mar2003"), iso_date("01Apr2004")

#         expected = [labels[0]]
#         expected = pd.DataFrame(expected).set_index(["parcel_id", "inspection_date"])

#         self.db.add_labels(labels)
#         actual = dataset.load_labels(start_date, end_date)
#         assert_frame_equal(expected, actual)

#     def test_inspection_same_day(self):
#         labels = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "viol_outcome": 0},
#                   {"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "viol_outcome": 1}]
#         start_date, end_date = iso_date("01Mar2003"), iso_date("01Apr2004")

#         expected = labels
#         expected = pd.DataFrame(expected).set_index(["parcel_id", "inspection_date"])

#         self.db.add_labels(labels)
#         actual = dataset.load_labels(start_date, end_date)
#         assert_frame_equal(expected, actual)


# class TestCrime(unittest.TestCase):

#     def setUp(self):
#         self.db = FeatureDatabase()

#     def tearDown(self):
#         self.db.close()

#     def make_expected_df(self, expected):
#         #if not imputations:
#         #    imputations = [0] * len(expected)
#         #for exp, imp in zip(expected, imputations):
#         #    exp["imputation_crime_rate_past_year"] = imp
#         return pd.DataFrame(expected).set_index(["parcel_id", "inspection_date"])


#     def test_one_crime_in_timerange(self):
#         crimes = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "crime_rate_past_year": 0.2}]
#         start_date, end_date = iso_date("01Mar2003"), iso_date("01Apr2004")

#         expected = crimes
#         expected = self.make_expected_df(expected)

#         self.db.add_crime(crimes)
#         actual = dataset.load_crime_features(["crime_rate_past_year"], start_date, end_date)
#         assert_frame_equal(expected, actual)

#     def test_two_crime_in_timerange(self):
#         crimes = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "crime_rate_past_year": 0.2},
#                   {"parcel_id": "abc", "inspection_date": iso_date("05Mar2004"), "crime_rate_past_year": 0.3}]
#         start_date, end_date = iso_date("01Mar2003"), iso_date("01Apr2004")

#         expected = crimes
#         expected = self.make_expected_df(expected)

#         self.db.add_crime(crimes)
#         actual = dataset.load_crime_features(["crime_rate_past_year"], start_date, end_date)
#         assert_frame_equal(expected, actual)

#     def test_inspection_duplicate(self):
#         crimes = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "crime_rate_past_year": 0.2},
#                   {"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "crime_rate_past_year": 0.2}]
#         start_date, end_date = iso_date("01Mar2003"), iso_date("01Apr2004")

#         expected = [crimes[0]]
#         expected = self.make_expected_df(expected)

#         self.db.add_crime(crimes)
#         actual = dataset.load_crime_features(["crime_rate_past_year"], start_date, end_date)
#         assert_frame_equal(expected, actual)

    #does this test work?
    # def test_two_crime_with_imputation(self):
    #     crimes = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "crime_rate_past_year": 0.2},
    #               {"parcel_id": "abc", "inspection_date": iso_date("05Mar2004"), "crime_rate_past_year": 0.2}]
    #     start_date, end_date = iso_date("01Mar2003"), iso_date("01Apr2004")

    #     expected = [{"parcel_id": "cde", "inspection_date": iso_date("01Mar2004"), "crime_rate_past_year": 0.2},
    #                 {"parcel_id": "abc", "inspection_date": iso_date("05Mar2004"), "crime_rate_past_year": 0.2}]
    #     expected = self.make_expected_df(expected)

    #     self.db.add_crime(crimes)
    #     actual = dataset.load_crime_features(["crime_rate_past_year"], start_date, end_date)
    #     assert_frame_equal(expected, actual)
    


class TestImputationSeries(unittest.TestCase):

    def make_input(self, index, values):
        return pd.Series(values, index=index, name="original")

    def make_expected(self, index, values_expected, imputed_expected):
        values_expected = pd.Series(values_expected, index=index, name="original")
        impute_expected = pd.Series(imputed_expected, index=index, name="imputation_original")
        expected = pd.concat([values_expected, impute_expected], axis=1)
        return expected

    def test_no_impute(self):
        index = ["bla", "blue", "blo"]
        values = [0.2, 0.4, 0.4]

        values_expected = [0.2, 0.4, 0.4]
        impute_expected = [0, 0, 0]
        expected = self.make_expected(index, values_expected, impute_expected)

        actual = util.mean_impute_series(self.make_input(index, values))
        assert_frame_equal(expected, actual)
        
    def test_impute_one(self):
        index = ["bla", "blue", "blo"]
        values = [0.2, np.nan, 0.4]

        values_expected = [0.2, 0.3, 0.4]
        impute_expected = [0, 1, 0]
        expected = self.make_expected(index, values_expected, impute_expected)

        actual = util.mean_impute_series(self.make_input(index, values))
        assert_frame_equal(expected, actual)

    def test_impute_two(self):
        index = ["bla", "blue", "blo"]
        values = [np.nan, np.nan, 0.4]

        values_expected = [0.4, 0.4, 0.4]
        impute_expected = [1, 1, 0]
        expected = self.make_expected(index, values_expected, impute_expected)

        actual = util.mean_impute_series(self.make_input(index, values))
        assert_frame_equal(expected, actual)

    @raises(Exception)
    def test_all_missing(self):
        index = ["bla", "blue", "blo"]
        values = [np.nan, np.nan, np.nan]

        util.mean_impute_series(self.make_input(index, values))


class TestImputationFrame(unittest.TestCase):

    def make_input(self, index, values_list):
        all_series = []
        for i, values in enumerate(values_list):
            all_series.append(pd.Series(values, index=index, name="original{}".format(i)))
        return pd.concat(all_series, axis=1)

    def make_expected(self, index, expected):
        all_series = []
        for i, (values_expected, imputed_expected) in enumerate(expected):
            all_series.append(pd.Series(values_expected, index=index, name="original{}".format(i)))
            if imputed_expected is not None:
                all_series.append(pd.Series(imputed_expected, index=index, name="imputation_original{}".format(i)))
        expected = pd.concat(all_series, axis=1)
        return expected

    def test_no_impute(self):
        index = ["bla", "blue", "blo"]
        values0 = [0.2, 0.4, 0.4]
        values1 = [0.4, 0.8, 0.8]
        values2 = [0.3, 0.0, 0.8]

        expected0 = values0, [0, 0, 0]
        expected1 = values1, [0, 0, 0]
        expected2 = values2, [0, 0, 0]
        expected = self.make_expected(index, [expected0, expected1, expected2])

        actual = util.mean_impute_frame(self.make_input(index, [values0, values1, values2]))
        assert_frame_equal(expected, actual)

    def test_impute_one_series(self):
        index = ["bla", "blue", "blo"]
        values0 = [0.2, 0.4, 0.4]
        values1 = [0.4, np.nan, 0.8]
        values2 = [0.3, 0.0, 0.8]

        expected0 = values0, [0, 0, 0]
        expected1 = [0.4, 0.6, 0.8], [0, 1, 0]
        expected2 = values2, [0, 0, 0]
        expected = self.make_expected(index, [expected0, expected1, expected2])

        actual = util.mean_impute_frame(self.make_input(index, [values0, values1, values2]))
        assert_frame_equal(expected, actual)

    def test_impute_two_series(self):
        index = ["bla", "blue", "blo"]
        values0 = [np.nan, 0.4, np.nan]
        values1 = [0.4, np.nan, 0.8]
        values2 = [0.3, 0.0, 0.8]

        expected0 = [0.4, 0.4, 0.4], [1, 0, 1]
        expected1 = [0.4, 0.6, 0.8], [0, 1, 0]
        expected2 = values2, [0, 0, 0]
        expected = self.make_expected(index, [expected0, expected1, expected2])

        actual = util.mean_impute_frame(self.make_input(index, [values0, values1, values2]))
        assert_frame_equal(expected, actual)

    def test_impute_three_series(self):
        index = ["bla", "blue", "blo"]
        values0 = [np.nan, 0.4, np.nan]
        values1 = [0.4, np.nan, 0.8]
        values2 = [0.3, 0.0, np.nan]

        expected0 = [0.4, 0.4, 0.4], [1, 0, 1]
        expected1 = [0.4, 0.6, 0.8], [0, 1, 0]
        expected2 = [0.3, 0.0, 0.15], [0, 0, 1]
        expected = self.make_expected(index, [expected0, expected1, expected2])

        actual = util.mean_impute_frame(self.make_input(index, [values0, values1, values2]))
        assert_frame_equal(expected, actual)

    @raises(Exception)
    def test_all_missing(self):
        index = ["bla", "blue", "blo"]
        values0 = [np.nan, np.nan, np.nan]
        values1 = [0.4, np.nan, 0.8]
        values2 = [0.3, 0.0, np.nan]

        util.mean_impute_frame(self.make_input(index, [values0, values1, values2]))

    def test_impute_subset(self):
        index = ["bla", "blue", "blo"]
        values0 = [np.nan, 0.4, np.nan]
        values1 = [0.4, np.nan, 0.8]
        values2 = [0.3, 0.0, np.nan]
        subset = ["original2"]

        expected0 = values0, None
        expected1 = values1, None
        expected2 = [0.3, 0.0, 0.15], [0, 0, 1]
        expected = self.make_expected(index, [expected0, expected1, expected2])

        actual = util.mean_impute_frame(self.make_input(index, [values0, values1, values2]), subset=subset)
        assert_frame_equal(expected, actual)

    def test_impute_empty_subset(self):
        index = ["bla", "blue", "blo"]
        values0 = [np.nan, 0.4, np.nan]
        values1 = [0.4, np.nan, 0.8]
        values2 = [0.3, 0.0, np.nan]
        subset = []

        expected0 = values0, None
        expected1 = values1, None
        expected2 = values2, None
        expected = self.make_expected(index, [expected0, expected1, expected2])

        actual = util.mean_impute_frame(self.make_input(index, [values0, values1, values2]), subset=subset)
        assert_frame_equal(expected, actual)

    def test_all_missing_not_in_subset(self):
        index = ["bla", "blue", "blo"]
        values0 = [np.nan, np.nan, np.nan]
        values1 = [0.4, np.nan, 0.8]
        values2 = [0.3, 0.0, np.nan]
        subset = ["original2"]

        expected0 = values0, None
        expected1 = values1, None
        expected2 = [0.3, 0.0, 0.15], [0, 0, 1]
        expected = self.make_expected(index, [expected0, expected1, expected2])

        actual = util.mean_impute_frame(self.make_input(index, [values0, values1, values2]), subset=subset)
        assert_frame_equal(expected, actual)