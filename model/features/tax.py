import pandas as pd
import numpy as np

def load_three_year_home_values(db_connection):
    taxes = ("SELECT inspections.parcel_id, inspections.inspection_date, "
             "year AS taxyear, "
             "        CAST(mkt_total_val AS INTEGER) AS mkt_total_val, "
             "        CAST(mkt_land_val AS INTEGER) AS mkt_land_val, "
             "        CAST(mkt_impr_val AS INTEGER) AS mkt_impr_val "
             " FROM parcels_inspections AS inspections "
             " JOIN public.tax_combined AS taxes "
             " ON inspections.parcel_id = taxes.parcel_id "
             "  AND EXTRACT(YEAR FROM inspections.inspection_date)"
             " > taxes.year "
             "  AND EXTRACT(YEAR FROM inspections.inspection_date)"
             " - 3 <= taxes.year;")

    taxes = pd.read_sql(taxes, con=db_connection)
    taxes = taxes.set_index(["parcel_id", "inspection_date"])
    return taxes


def load_three_year_foreclosures(db_connection):
    foreclosures = ("SELECT inspections.parcel_id, "
                    "inspections.inspection_date, "
                    "taxes.year, taxes.forcl_flag AS foreclosure "
                    " FROM parcels_inspections AS inspections "
                    " JOIN public.tax_foreclosure AS taxes "
                    " ON inspections.parcel_id = taxes.parcel_id "
                    "  AND EXTRACT(YEAR FROM inspections.inspection_date)"
                    " > taxes.year "
                    "  AND EXTRACT(YEAR FROM inspections.inspection_date)"
                    " - 3 <= taxes.year;")

    foreclosures = pd.read_sql(foreclosures, con=db_connection)
    foreclosures = foreclosures.set_index(["parcel_id", "inspection_date"])
    return foreclosures


def calculate_means(values):
    values = values[["mkt_total_val", "mkt_land_val", "mkt_impr_val"]]
    means = values.reset_index().groupby(["parcel_id",
                                          "inspection_date"]).mean()
    means = means.rename(columns={"mkt_total_val": "mean_market_value",
                                  "mkt_land_val": "mean_land_value",
                                  "mkt_impr_val": "mean_impr_value"})
    return means


def calculate_value_changes(group):

    first_year = group["taxyear"].argmin()
    last_year = group["taxyear"].argmax()

    # tax data only for one year -> change is undefined
    if first_year == last_year:
        return pd.Series({"change_market_value": np.nan,
                          "change_land_value": np.nan,
                          "change_impr_value": np.nan})

    first_year_values = group.loc[first_year][["mkt_total_val",
                                               "mkt_land_val",
                                               "mkt_impr_val"]]
    last_year_values = group.loc[last_year][["mkt_total_val",
                                             "mkt_land_val",
                                             "mkt_impr_val"]]

    value_changes = (last_year_values - first_year_values)

    return pd.Series({"change_market_value": value_changes["mkt_total_val"],
                      "change_land_value": value_changes["mkt_land_val"],
                      "change_impr_value": value_changes["mkt_impr_val"]})


def calculate_relative_value_changes(group):
    first_year = group["taxyear"].argmin()
    last_year = group["taxyear"].argmax()

    # tax data only for one year -> change is undefined
    if first_year == last_year:
        return pd.Series({"rel_change_market_value": np.nan,
                          "rel_change_land_value": np.nan,
                          "rel_change_impr_value": np.nan})

    first_year_values = group.loc[first_year][["mkt_total_val",
                                               "mkt_land_val",
                                               "mkt_impr_val"]]
    last_year_values = group.loc[last_year][["mkt_total_val",
                                             "mkt_land_val",
                                             "mkt_impr_val"]]

    value_changes = (last_year_values - first_year_values) / first_year_values
    value_changes = value_changes.replace([np.inf, -np.inf], np.nan)

    return pd.Series({"rel_change_market_value":
                      value_changes["mkt_total_val"],
                      "rel_change_land_value": value_changes["mkt_land_val"],
                      "rel_change_impr_value": value_changes["mkt_impr_val"]})


def count_foreclosed_years(group):
    group = group["foreclosure"].replace({True: 1.0, False: 0.0})
    return pd.Series({"tax_foreclosure": group.sum()})


def make_tax_features(db_connection):
    """
    Make different tax features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """

    features = []

    values = load_three_year_home_values(db_connection)

    means = calculate_means(values)
    features.append(means["mean_market_value"])
    features.append(means["mean_land_value"])
    features.append(means["mean_impr_value"])

    changes = values.reset_index().groupby(["parcel_id",
                                            "inspection_date"]).apply(
                                        calculate_value_changes)
    features.append(changes["change_market_value"])
    features.append(changes["change_land_value"])
    features.append(changes["change_impr_value"])

    changes = values.reset_index().groupby(["parcel_id",
                                            "inspection_date"]).apply(
                                        calculate_relative_value_changes)
    features.append(changes["rel_change_market_value"])
    features.append(changes["rel_change_land_value"])
    features.append(changes["rel_change_impr_value"])

    foreclosures = load_three_year_foreclosures(db_connection)
    foreclosures = foreclosures.reset_index().groupby(["parcel_id",
                                                  "inspection_date"]).apply(
                                                  count_foreclosed_years)
    features.append(foreclosures["tax_foreclosure"])

    features = pd.concat(features, axis=1)
    return features
