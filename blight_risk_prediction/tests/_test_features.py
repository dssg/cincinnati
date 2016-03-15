import datetime
import unittest

import numpy as np
from numpy.testing import assert_array_equal, assert_equal
import pandas as pd

from features import crime
from lib_cinci.test_utils import RawDatabase, date, timestamp, assert_frame_equal


class TestCrime(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_crimerate_df(self, crimes):
        crimes = pd.DataFrame(crimes, columns=["date_reported", "agg_area", "count"])
        crimes["year_reported"] = crimes["date_reported"].apply(lambda d: date(d).year)
        crimes["month_reported"] = crimes["date_reported"].apply(lambda d: date(d).month)
        crimes = crimes.set_index("agg_area")
        return crimes[["year_reported", "month_reported", "count"]]

    def make_parcels_df(self, parcels):
        parcels = pd.DataFrame(parcels, columns=["parcel_id", "inspection_date", "agg_area"])
        parcels["inspection_date"] = parcels["inspection_date"].apply(lambda d: date(d))
        return parcels

    def make_population_df(self, population):
        population = pd.DataFrame(population, columns=["area", "population"])
        population = population.set_index("area")
        return population

    def make_expected_df(self, expected):
        expected = pd.DataFrame(expected, columns=["parcel_id",  "inspection_date", "crime_rate"])
        expected["inspection_date"] = expected["inspection_date"].apply(lambda d: date(d))
        expected = expected.set_index(["parcel_id",  "inspection_date"])
        return expected

    # numpy assert_array_almost_equal can not deal with strings
    def assert_array_almost_equal(self, expected, actual):
        for exp, act in zip(expected, actual):
            for e, a in zip(exp, act):
                assert_equal(e, a)

    def test_one_inspection_one_crime(self):
        crimes = [("16Sep2014", "tract567", 3)]
        parcels = [("parcelA", "01Dec2014", "tract567")]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", date("01Dec2014"), 3 / float(1234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_one_inspection_one_crime_missing_tract(self):
        crimes = [("16Sep2014", "tract567", 3)]
        parcels = [("parcelA", "01Dec2014", "tract567")]
        population = []
        window = datetime.timedelta(days=365)

        expected = [("parcelA", date("01Dec2014"), np.nan)]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_one_inspection_several_crimes(self):
        crimes = [("16Sep2014", "tract567", 3),
                  ("18Oct2014", "tract567", 1)]
        parcels = [("parcelA", "01Dec2014", "tract567")]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", date("01Dec2014"), 4 / float(1234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_one_inspection_empty_crimes(self):
        crimes = []
        parcels = [("parcelA", "01Dec2014", "tract567")]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", timestamp("01Dec2014"), 0.0)]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_one_inspection_no_crimerate_in_range(self):
        crimes = [("16Sep2012", "tract567", 3),
                  ("18oct2013", "tract567", 1)]
        parcels = [("parcelA", "01Dec2014", "tract567")]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", date("01Dec2014"), 0)]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_several_inspections_same_parcel_several_crimes(self):
        crimes = [("16Sep2014", "tract567", 3),
                  ("18Oct2014", "tract567", 1)]
        parcels = [("parcelA", "01Dec2014", "tract567"),
                   ("parcelA", "18Nov2014", "tract567"),]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", timestamp("01Dec2014"), 4 / float(1234)),
                    ("parcelA", timestamp("18Nov2014"), 4 / float(1234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_several_inspections_same_parcel_one_crime_in_range(self):
        crimes = [("16Sep2014", "tract567", 3),
                  ("18Dec2014", "tract567", 1)]
        parcels = [("parcelA", "01Dec2014", "tract567"),
                   ("parcelA", "18Nov2014", "tract567")]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", timestamp("01Dec2014"), 3 / float(1234)),
                    ("parcelA", timestamp("18Nov2014"), 3 / float(1234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_several_inspections_same_parcel_one_crime_in_range_for_one_two_for_other(self):
        crimes = [("16Sep2014", "tract567", 3),
                  ("20Nov2013", "tract567", 1)]
        parcels = [("parcelA", "01Dec2014", "tract567"),
                   ("parcelA", "18Oct2014", "tract567"),]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", timestamp("01Dec2014"), 3 / float(1234)),
                    ("parcelA", timestamp("18Oct2014"), 4 / float(1234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_several_inspections_several_parcels_same_tract(self):
        crimes = [("16Sep2014", "tract567", 3),
                  ("18Oct2014", "tract567", 1)]
        parcels = [("parcelA", "01Dec2014", "tract567"),
                   ("parcelB", "18Nov2014", "tract567"),]
        population = [("tract567", 1234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", timestamp("01Dec2014"), 4 / float(1234)),
                    ("parcelB", timestamp("18Nov2014"), 4 / float(1234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_several_inspections_several_parcels_different_tract(self):
        crimes = [("16Sep2014", "tract567", 3),
                  ("18Oct2014", "tract568", 1),
                  ("14Jul2014", "tract568", 6)]
        parcels = [("parcelA", "01Dec2014", "tract567"),
                   ("parcelB", "18Nov2014", "tract568"),]
        population = [("tract567", 1234),
                      ("tract568", 234)]
        window = datetime.timedelta(days=365)

        expected = [("parcelA", timestamp("01Dec2014"), 3 / float(1234)),
                    ("parcelB", timestamp("18Nov2014"), 7 / float(234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)

    def test_six_month_window(self):
        crimes = [("16Sep2014", "tract567", 3),
                  ("18Sep2014", "tract568", 1),
                  ("14Mar2014", "tract568", 6)]
        parcels = [("parcelA", "01Dec2014", "tract567"),
                   ("parcelB", "18Apr2014", "tract568"),]
        population = [("tract567", 1234),
                      ("tract568", 234)]
        window = datetime.timedelta(days=180)

        expected = [("parcelA", timestamp("01Dec2014"), 3 / float(1234)),
                    ("parcelB", timestamp("18Apr2014"), 6 / float(234))]

        actual =crime.crimerate_in_aggregation_area(self.make_parcels_df(parcels), self.make_crimerate_df(crimes),
                                       self.make_population_df(population), window)
        actual = actual.reset_index()[["parcel_id", "inspection_date", "crime_rate"]].values

        self.assert_array_almost_equal(expected, actual)
        assert_array_equal(expected, actual)
