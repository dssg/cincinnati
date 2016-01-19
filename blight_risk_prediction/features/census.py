#!/usr/bin/env python
import numpy as np
import pandas as pd
from blight_risk_prediction import util, colmap

def make_census_features(db_connection):
    """
    Get census features for parcels

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.

    Join census feature table with parcel_id by block groups and tracts
    """

    query = ("SELECT parcels_spt.parcelid as parcel_id, census.* "
             "FROM shape_files.census_features as census JOIN "
             "shape_files.parcelid_blocks_grp_tracts_nhoods as parcels_spt "
             "on census.tract = parcels_spt.tract "
             "and census.block_group = parcels_spt.block_group;")

    df = pd.read_sql(query, con=db_connection)

    return df
