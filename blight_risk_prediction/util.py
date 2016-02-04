#!/usr/bin/env python
import logging
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import datetime

logger = logging.getLogger()

years = ['2007', '2008', '2009', '2010', '2011',
         '2012', '2013', '2014', '2015']

tax_dfs = {'2007': 'taxes07', '2008': 'taxes08', '2009': 'taxes09',
           '2010': 'taxes10', '2011': 'taxes11', '2012': 'taxes12',
           '2013': 'taxes13', '2014': 'taxes14', '2015': 'taxes15'}


def format_parcels_list(parcels):
    parcels = ["'{}'".format(pid) for pid in parcels]
    parcels = ", ".join(parcels)
    return parcels

def get_taxes(year, engine):
    tax_db = {'2007': 'taxes_2007', '2008': 'taxes_2008', '2009': 'taxes_2009',
              '2010': 'taxes_2010', '2011': 'taxes_2011', '2012': 'taxes_2012',
              '2013': 'taxes_2013', '2014': 'taxes_2014', '2015': 'taxes_2015'}

    if year != '2015':
        query = ('SELECT "PARCEL_ID", "MKT_TOTAL_VAL", "ANNUAL_TAXES", ' +
            '"ZIPCODE" FROM public.' + tax_db[year] + ' LIMIT 400000')
    else:
        query = ('SELECT "PARCEL", "MKT_TOTAL_VAL", "ANNUAL_TAXES", ' +
            '"LOC_ZIP" FROM public.' + tax_db[year] + ' LIMIT 400000')
    df = pd.read_sql_query(query, con=engine)
    return df


def make_short_zip(year, df):
    if year != '2015':
        df['SHORTZIP'] = df.ZIPCODE.str[:5]
    else:
        df['SHORTZIP'] = df.LOC_ZIP.str[:5]
    return df


def get_dummies(series, possible_values):
    """
    Converts a categorical variable to a set of binary variables.

    This function is modeled after the pandas get_dummies function.
    The difference to the pandas version is that this
    function guarantees that there will be a column for each
    possible value of the categorical variable, i.e. the number
     (and ordering) of the binary columns is always the same

    E.g. assume the variable can take values val1, val2 and val3
    and but the input series only contains val1 and val3
      - in pandas' get_dummies the resulting data frame will
      have only two columns val1 and val3
      - with this function the resulting data frame will
      have three columns val1, val2, val3. val2 will be filled with 0

    :param series:
    :param possible_values: The list of values the categorical variable
    can take.
    :return: A pandas dataframe with as many binary columns as there
    are possible values.
    """

    def make_dummies(value):
        if isinstance(value, float) and np.isnan(value):
            dummy = pd.Series(np.nan, index=possible_values)
            return dummy
        else:
            if value not in possible_values:
                raise ValueError("{} is not in allowed list of values {}".format(value, possible_values))
            dummy = pd.Series(0, index=possible_values)
            dummy[value] = 1
            return dummy

    if len(series) == 0:
        return pd.DataFrame([], columns=possible_values)
    else:
        return series.apply(make_dummies)


def mean_impute_series(series):

    is_finite = np.isfinite(series.values)

    if sum(is_finite) == 0:
        raise ArithmeticError("All values missing for {} can not impute".format(series.name))

    mean_val = np.mean(series.ix[is_finite])
    series = series.fillna(mean_val)
    # values = series.values
    # values[is_finite == False] = mean_val

    track_impute = pd.Series(is_finite, index=series.index,
                             name="imputation_{}".format(series.name))
    track_impute = track_impute.map({False: 1, True: 0})

    perc_imputed = round(sum(track_impute)/float(len(series)), 2)*100
    logger.debug("Imputed {}% of values for {}".format(perc_imputed, series.name))

    merged = pd.concat([series, track_impute], axis=1)
    return merged


def mean_impute_frame(frame, subset=None):
    """

    :param frame:
    :param subset: List of column names to impute.
     If subset=None, all columns will be imputed.
    :return:
    """
    if subset is None:
        subset = frame.columns

    pd.set_option('mode.use_inf_as_null', True)
    frame_imputed = [mean_impute_series(frame[col])
                     if col in subset else frame[col] for col in frame.columns]
    frame_imputed = pd.concat(frame_imputed, axis=1)

    # Drop rows with NaNs - needed?
    # dataset = dataset.dropna()
    # Also drop infinities - needed?
    # dataset = dataset[dataset.notnull() == True]
    return frame_imputed


def population_in_tracts():
    engine = create_engine(uri)
    populations = ("SELECT tract, sum(\"P0010001\") AS population "
                   "FROM shape_files.census_pop_housing "
                   "GROUP BY tract")
    populations = pd.read_sql(populations, con=engine)
    populations = populations.set_index("tract")
    return populations
