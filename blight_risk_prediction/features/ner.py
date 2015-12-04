#!/usr/bin/env python

import numpy as np
import pandas as pd


from blight_risk_prediction import util, colmap


def make_owner_features(db_connection):
    """
    Get the number of years that a home was owned by
    a corporation in last three years.

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """

    query = ("SELECT inspections.inspection_date, taxes.* "
             "FROM parcels_inspections AS inspections "
             "JOIN public.taxes_owners AS taxes "
             "ON inspections.parcel_id = taxes.parcel_id")
    df = pd.read_sql(query, con=db_connection)

    for year in colmap.insp_years:
        indices_this_year = df.inspection_date.dt.year == int(year)
        year_range = range(int(year[2:]) - 3, int(year[2:]))

        if int(year) == 2008:
            num_org = df[["owner_2007", "parcel_id"]]
        elif int(year) == 2009:
            num_org = df[["owner_2007", "owner_2008"]]
        elif int(year) >= 2010:
            num_org = df[['owner_20' + str(y).zfill(2) for y in year_range]]

        try:
            computation = num_org.apply(lambda row: 
                                        len(row[row == 'ORGANIZATION']), axis=1)
            df.ix[indices_this_year, "owner_ner"] = computation
        except:
            df.ix[indices_this_year, "owner_ner"] = np.nan

    return df
