#!/usr/bin/env python

import pandas as pd
import numpy as np

from blight_risk_prediction import util


def generate_labels():
    """
    Generate labels for all the parcels in the inspection view.

    Input:

    Output:
    A pandas dataframe with one row per inspection and three columns:
        "parcel_id", "inspection_date", "viol_outcome"
    """

    engine = util.get_engine()

    # SQL query to pull down all parcels with a inspection
    all_insp_query = ("SELECT parcel.parcel_no, events.number_key, "
                      "events.date "
                      "FROM inspections_views.events AS events "
                      "JOIN inspections_views.number_key2parcel_no AS parcel "
                      "ON events.number_key = parcel.number_key "
                      "WHERE events.comp_type = 'CBHCODE' "
                      "AND events.event = 'Initial inspection'")

    df_insp = pd.read_sql_query(all_insp_query, con=engine)

    # SQL query to pull down all parcels with a violation
    all_viol_query = ("SELECT parcel.parcel_no, events.number_key, "
                      "events.date "
                      "FROM inspections_views.events AS events "
                      "JOIN inspections_views.number_key2parcel_no AS parcel "
                      "ON events.number_key = parcel.number_key "
                      "WHERE events.comp_type = 'CBHCODE' "
                      "AND (events.event = 'Orders issued' OR "
                      "events.event = 'Civil 2' "
                      "OR events.event = 'Civil 1' OR events.event "
                      "= 'Final notice' OR "
                      "events.event = 'Pre-prosecution status' "
                      "OR events.event = 'Prosecutor approves')"
                      )

    df_viol = pd.read_sql_query(all_viol_query, con=engine)

    df_insp.columns = ['parcel_insp', 'number_key', 'date_insp']
    df_viol.columns = ['parcel_viol', 'number_key', 'date_viol']
    df_viol['Label_viol'] = 1
    df_insp['Label_insp'] = 0
    has_violation = df_insp.number_key.isin(df_viol.number_key)

    # If number key from df_insp appears in df_viol, then
    # that case HAS a violation.
    # If number key from df_insp DOES NOT appear in
    # df_viol then it DOES NOT have a violation.
    df_insp['Label'] = has_violation
    convert_to_nums = df_insp.applymap(lambda x: 1 if x else 0)
    df_insp['Label'] = convert_to_nums['Label']

    # Tag parcels that aren't in the inspection list
    # as violations (Reported -> Violation)
    # those parcels that are not in the list should
    # be appended as violations with the date taken
    # from the violations table.
    # TODO: Examine the t_inspection - t_violation
    # distribution and cut out the outliers
    viol_parcels_w_insp = df_viol.number_key.isin(df_insp.number_key)
    df_insp = df_insp.drop('Label_insp', axis=1)
    df_viol = df_viol.drop('Label_viol', axis=1)
    df_viol['Label'] = 1
    df_noinsp = df_viol[viol_parcels_w_insp == False]
    df_noinsp.columns = ['parcel_insp', 'number_key', 'date_insp', 'Label']

    df = df_insp.append(df_noinsp, ignore_index=True)
    df = df.fillna(0)

    # Format dataframe to match database table
    df = df.drop('number_key', axis=1)  # don't need number key anymore
    df.columns = ['parcel_id', 'inspection_date', 'viol_outcome']

    return df


def make_fake_inspections_all_parcels_cincy(fake_inspection_date):
    """
    Create a new dataframe that contains every parcel
    in Cincinnati. This frame resembles the one
    that is created by generate_labels() but it does
    not have an "outcome" column. The reason is that we are not
    actually listing inspections here, but pretend that
    we are investigating each of the cincinnati parcels on
    the given fake_inspection_date. We will (in some other
    function) generate features for each of these fake
    inspections.

    parcel_id, inspection_date
    1234,      fake_inspection_date
    26377,     fake_inspection_date

    :param fake_inspection_date:
    :return: Pandas dataframe with one row per (fake) inspection
    and two columns: "parcel_id", "inspection_date"
    """

    # get all cincinnati parcels
    parcels = ("SELECT DISTINCT(parcelid) AS parcel_id "
               "FROM shape_files.parcels_cincy")
    engine = util.get_engine()
    parcels = pd.read_sql(parcels, con=engine)

    # add column with the fake inspection date
    parcels["inspection_date"] = pd.Series(fake_inspection_date,
                                           index=parcels.index)

    # add empty column with outcome
    parcels["viol_outcome"] = pd.Series(np.nan, index=parcels.index)

    return parcels
