from datetime import timedelta
import logging


import numpy as np
import pandas as pd
from blight_risk_prediction import util


logger = logging.getLogger(__name__)

first_ever_crime = {"year": 2004, "month": 1}
last_ever_crime = {"year": 2014, "month": 12}
months_with_crime = 11*12


def number_of_months_since_first_crime(date_year, date_month):
    years_passed = date_year - first_ever_crime["year"]
    months_passed = date_month - first_ever_crime["month"]
    # above line only works because first ever crime in January
    months_passed = years_passed*12 + months_passed

    months_passed = max(0, months_passed)
    months_passed = min(months_with_crime - 1, months_passed)
    return months_passed


def make_fast_crime_lookup_table(crimes):
    """
    Create a fast crime-rate lookup function
    :param crimes: A dataframe with crimes aggregated per month and area, e.g.
                  year_reported  month_reported  count
        agg_area
        123444             2004               1      7
        188992             2005               3     89
        001119             2008               9     53
        192920             2004               1     66
        122726             2004               1     27
    :return: A dict of lists
    """

    # a naive lookup of crimes in the given pandas crime data frame is O(n^2)
    #   1. find all rows for the given area O(n)
    #   2. of these, find all rows that fall into the time window O(n)

    # this is too slow, transform the crimes data frame as follows
    #  A. make a dict of {area: crimes_for_area} -> O(1)
    #  B. convert crimes_for_area into an array where each
    #     entry corresponds to a month such as
    #        [num_crimes_Jan_2004, num_crimes_Feb_2004,
    #         num_crimes_Mar_2004, ..., num_crimes_Dec_2014]
    #     now counting the number of crimes in a time window
    #     is simply to sum up the relevant months -> O(1)

    # this implements B from above
    index = pd.Index(range(months_with_crime))

    def make_lookup_array(crimes_for_area):
        crimes_for_area = crimes_for_area.copy()
        crimes_for_area["num_months_passed"] = \
            crimes_for_area[["year_reported", "month_reported"]].apply(
                lambda row: number_of_months_since_first_crime(
                    row["year_reported"], row["month_reported"]), axis=1)
        crimes_for_area = crimes_for_area.set_index("num_months_passed")
        crimes_for_area = crimes_for_area.reindex(index).fillna(0)
        return crimes_for_area["count"].values

    # this implements A from above
    crimes = {area: make_lookup_array(grp) for area, grp
              in crimes.groupby(crimes.index)}

    return crimes


def configure_population_lookup(population_tracts):
    def perform(tract):
        if not tract in population_tracts.index:
            return np.nan
        return population_tracts.loc[tract]
    return perform


def load_tract_data(db_connection, only_guncrimes=False):
    def load_crimes():
        logger.debug("Read crimes per census tract")
        if only_guncrimes:
            crimes = ("SELECT EXTRACT(YEAR FROM date_reported) AS "
                      "year_reported, "
                      "       EXTRACT(MONTH FROM date_reported) AS "
                      "month_reported,  "
                      "       tract AS agg_area, "
                      "       count(*) "
                      "FROM public.crime_geocoded "
                      "WHERE weapon LIKE '%%GUN%%'"
                      "GROUP BY year_reported, month_reported, tract")
        else:
            crimes = ("SELECT EXTRACT(YEAR FROM date_reported) "
                      "AS year_reported, "
                      "       EXTRACT(MONTH FROM date_reported) "
                      "AS month_reported,  "
                      "       tract AS agg_area, "
                      "       count(*) "
                      "FROM public.crime_geocoded "
                      "GROUP BY year_reported, month_reported, tract")

        crimes = pd.read_sql(crimes, con=db_connection)
        crimes = crimes.dropna(subset=["agg_area"]).set_index("agg_area")
        return crimes

    def load_parcels():
        logger.debug("Read parcels")
        parcels = ("SELECT parcel_id, "
                   "       inspection_date, "
                   "       tract AS agg_area "
                   "FROM parcels_inspections AS parcels "
                   "JOIN shape_files.parcelid_blocks_grp_tracts_nhoods "
                   "AS shape "
                   "ON parcels.parcel_id = shape.parcelid")

        parcels = pd.read_sql(parcels, con=db_connection)
        return parcels

    return load_crimes(), load_parcels(), util.population_in_tracts()


def load_blockgroup_data(db_connection):
    def load_crimes():
        crimes = ("SELECT EXTRACT(YEAR FROM date_reported) "
                  "AS year_reported, "
                  "       EXTRACT(MONTH FROM date_reported) "
                  "AS month_reported,  "
                  "       CONCAT(tract, blkgrp) AS agg_area, "
                  "       count(*) "
                  "FROM public.crime_geocoded "
                  "GROUP BY year_reported, month_reported, tract, blkgrp")

        crimes = pd.read_sql(crimes, con=db_connection)
        crimes = crimes.dropna(subset=["agg_area"]).set_index("agg_area")
        return crimes

    def load_parcels():
        parcels = ("SELECT parcel_id, "
                   "       inspection_date, "
                   "       CONCAT(tract, blkgrp) AS agg_area "
                   "FROM parcels_inspections AS parcels "
                   "JOIN shape_files.parcelid_blocks_grp_tracts_nhoods "
                   "AS shape "
                   "ON parcels.parcel_id = shape.parcelid")

        parcels = pd.read_sql(parcels, con=db_connection)
        return parcels

    return load_crimes(), load_parcels(), util.population_in_tracts()


def crimerate_in_aggregation_area(parcels, crimes, population, window_size):

    crimes = make_fast_crime_lookup_table(crimes)

    def count_crimes_for_inspection(row):

        if not row["agg_area"] in crimes:
            return 0.0

        start_time = row["inspection_date"] - window_size
        start_index = number_of_months_since_first_crime(start_time.year,
                                                         start_time.month)

        end_time = row["inspection_date"]
        end_index = number_of_months_since_first_crime(end_time.year,
                                                       end_time.month)

        relevant_crimes = crimes[row["agg_area"]]
        num_crimes = sum(relevant_crimes[start_index:end_index])
        return num_crimes

    parcels["crimes"] = parcels.apply(count_crimes_for_inspection, axis=1)

    tract_lookup = configure_population_lookup(population)
    parcels["population"] = parcels["agg_area"].apply(tract_lookup)
    parcels["crime_rate"] = parcels["crimes"] / parcels["population"]

    parcels = parcels.set_index(["parcel_id", "inspection_date"])

    return parcels["crime_rate"]


def make_crime_features(db_connection):
    """
    Create features that aggregate crime over the area a parcel is in

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per parcels and one column per feature.
    """
    crime_features = []

    crimes, parcels, population = load_tract_data(db_connection)

    logger.debug("Calculate crime rate last year")
    window = timedelta(days=365)
    rate = crimerate_in_aggregation_area(parcels, crimes, population, window)
    rate.name = "crime_rate_1yr"
    crime_features.append(rate)
    logger.debug("... finished")

    logger.debug("Calculate crime rate last 3 years")
    window = timedelta(days=365*3)
    rate = crimerate_in_aggregation_area(parcels, crimes, population, window)
    rate.name = "crime_rate_3yr"
    crime_features.append(rate)
    logger.debug("... finished")

    crimes, parcels, population = load_tract_data(db_connection,
                                                  only_guncrimes=True)

    logger.debug("Calculate gun crime rate last year")
    window = timedelta(days=365)
    rate = crimerate_in_aggregation_area(parcels, crimes, population, window)
    rate.name = "crime_rate_1yr_guns"
    crime_features.append(rate)
    logger.debug("... finished")

    logger.debug("Calculate gun crime rate last 3 years")
    window = timedelta(days=365*3)
    rate = crimerate_in_aggregation_area(parcels, crimes, population, window)
    rate.name = "crime_rate_3yr_guns"
    crime_features.append(rate)
    logger.debug("... finished")

    crime_features = pd.concat(crime_features, axis=1)
    return crime_features
