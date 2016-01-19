#!/usr/bin/env python
import numpy as np
import pandas as pd
from blight_risk_prediction import util


def make_year_built(db_connection):
    """
    Get the year a home was built.

    Input:
    db_connection: connection to postgres database. "set schema ..."
                   must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per parcels and one column per feature.
    """

    query = ("SELECT inspections.parcel_id, parcels.year_built "
             "FROM features.parcels_inspections AS inspections "
             "JOIN public.bld_info AS parcels "
             "ON parcels.parcel_id = inspections.parcel_id")

    df = pd.read_sql(query, con=db_connection)
    df = df.set_index("parcel_id")

    return df


def make_size_of_prop(db_connection):
    """
    Get the size of a property

    Input:
    db_connection: connection to postgres database. "set schema ..."
                   must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per parcels and one column per feature.
    """

    query = ("SELECT inspections.parcel_id, parcels.area "
             "FROM parcels_inspections AS inspections "
             "JOIN shape_files.parcels_cincy AS parcels "
             "ON parcels.parcelid = inspections.parcel_id")

    df = pd.read_sql(query, con=db_connection)
    df = df.set_index("parcel_id")

    return df


def make_house_type_features(db_connection):
    """
    Get information whether a house is a single-family,
    two-family, three-family, multi-family home or mixed
    used (residential + commercial)

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per parcels and one column per feature.
    """

    query = ("SELECT inspections.parcel_id, parcels.class "
             "FROM parcels_inspections AS inspections "
             "JOIN shape_files.parcels_cincy AS parcels "
             "ON parcels.parcelid = inspections.parcel_id")

    df = pd.read_sql(query, con=db_connection)
    df = df.set_index("parcel_id")

    # map use code to type of home
    use_codes = {423: "mixed-used",
                 510: "single-family",
                 520: "two-family",
                 530: "three-family",
                 550: "multi-family",
                 554: "multi-family",
                 552: "multi-family",
                 599: "multi-family"}
    df["type"] = df["class"].apply(lambda cl: use_codes.get(cl, np.nan))

    df = util.get_dummies(df["type"], possible_values=["single-family",
                                                       "two-family",
                                                       "three-family",
                                                       "multi-family",
                                                       "mixed-use"])
    df = df.fillna(0)

    return df
