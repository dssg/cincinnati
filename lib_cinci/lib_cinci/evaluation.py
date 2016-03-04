from sklearn_evaluation.metrics import precision_at
from copy import deepcopy

from sqlalchemy import create_engine
from lib_cinci.db import uri
import pandas as pd
from scipy import stats

'''
    This file provides utility functions to evaluate
    model predictions
'''

def add_flags_to_predictions_df(df):
    '''
        Given a data frame with the following format:
            - Indexes: parcel_id, inspection_date
            - Columns: prediction, viol_outcome

        Attach columns with various metrics and flags
    '''
    #Copy df to avoid overwriting
    df = deepcopy(df)

    #Calculate precisions at 1 and 10 percent
    prec1, cutoff1 = precision_at(df.viol_outcome, df.prediction, percent=0.01)
    prec10, cutoff10 = precision_at(df.viol_outcome, df.prediction, percent=0.1)

    #Add columns
    df['top_1'] = df.prediction.map(lambda x: x>= cutoff1)
    df['top_10'] = df.prediction.map(lambda x: x>= cutoff10)
    df['tp_top_1'] = df.top_1 & df.viol_outcome
    df['tp_top_10'] = df.top_10 & df.viol_outcome
    df['fp_top_1'] = df.top_1 & ~df.viol_outcome
    df['fp_top_10'] = df.top_10 & ~df.viol_outcome
    return df

def add_latlong_to_df(df):
    '''
        Return a predictions data frame with latitude and longitude columns
        for each parcel. The DatFrame passed as parameter is expected to
        have a parcel_id index.

        This method is not memory efficient since it loads
        all parcels into memory, but it makes easier to retrieve lat,long.
        Use it responsibly.
    '''
    e = create_engine(uri)
    parcels = pd.read_sql_table('parcels_cincy', e,
        schema='shape_files',
        columns=['latitude', 'longitude'],
        index_col='parcelid')
    parcels.index.rename('parcel_id', inplace=True)
    return df.join(parcels)

def load_violations_for(start_year, end_year=None):
    '''
        Load violations that happened between start_year and end_year,
        returns a DataFrame with parcel_id, inspection_date, latitude, 
        longitude. Takes data from features schema, which has all
        inspections done.
    '''
    #If only one parameter is passed, set end_year
    #to the value of start_year
    end_year = start_year if end_year is None else end_year
    e = create_engine(uri)
    q='''
        SELECT
            insp.parcel_id, insp.inspection_date,
            parc.latitude, parc.longitude
        FROM features.parcels_inspections AS insp
        JOIN shape_files.parcels_cincy AS parc
        ON insp.parcel_id=parc.parcelid
        WHERE viol_outcome=1
        AND EXTRACT(YEAR FROM inspection_date)>=%(start_year)s
        AND EXTRACT(YEAR FROM inspection_date)<=%(end_year)s
    '''
    viol = pd.read_sql(q, e,
        columns=['latitude', 'longitude'],
        params={'start_year':start_year
        , 'end_year':end_year})
    return viol

def add_percentile_column(df, column_name):
    '''
        Given a DataFrame and a column_name
	return a new DataFrame with a new column including
	the percentile for the value in column_name 
    '''
    df = deepcopy(df)
    col_vals = df[column_name]
    perc_col_name = '{}_percentile'.format(column_name)
    df[perc_col_name] = [stats.percentileofscore(col_vals, value, 'rank') for value in col_vals]
    return df
