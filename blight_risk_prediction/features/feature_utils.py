import pandas as pd
from string import Template
import os
from sqlalchemy import create_engine
from dstools.db import uri
from dstools.config import load
import logging
import logging.config
import re
import logging
import logging.config
from dstools.config import load

#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

#This file provides generic functions
#to generate spatiotemporal features
def format_column_names(columns, prefix=None):
    #Get rid of non alphanumeric characters
    #and capital letters
    f = lambda s: re.sub('[^0-9a-zA-Z]+', '_', s).lower()
    names = columns.map(f)
    names = pd.Series(names).map(lambda s: '{}_{}'.format(prefix, s)) if prefix else names
    return names

#Utility function to see which tables already exist in schema
def tables_in_schema(con, schema):
    q = '''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema=%s;
    '''
    cur = con.cursor()
    cur.execute(q, [schema])
    tuples = cur.fetchall()
    names = [t[0] for t in tuples]
    return names

def columns_for_table_in_schema(con, table, schema):
    q = '''
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s
        AND table_name   = %s;
    '''
    cur = con.cursor()
    cur.execute(q, [schema, table])
    tuples = cur.fetchall()
    #names = [t[0] for t in tuples]
    return tuples

def make_load_nmonths_table_from_template(con, dataset, date_column,
                                     n_months, max_dist,
                                     template):
    path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
                        'blight_risk_prediction',
                        'features',
                        template)
    #Load template with SQL statement
    with open(path_to_template, 'r') as f:
        sql_script = Template(f.read())
    #Replace values in template
    sql_script = sql_script.substitute(TABLE_NAME=table_name,
                                       DATASET=dataset,
                                       DATE_COLUMN=date_column,
                                       N_MONTHS=n_months,
                                       MAX_DIST=max_dist)
    #Run the code using the connection
    #this is going to take a while
    con.cursor().execute(sql_script)
    #Commit changes to db
    con.commit()

def load_nmonths_table_from_template(con, dataset, date_column,
                                     n_months, max_dist,
                                     template, columns='all'):
    '''
        Load inspections table matched with events that happened X months
        before. Returns pandas dataframe with the data loaded
    '''
    #Create a cursor
    cur = con.cursor()

    #Get the current schema
    cur.execute('SELECT current_schema;')
    current_schema = cur.fetchone()[0]

    #Build the table name
    table_name = ('insp2{dataset}_{n_months}months'
                  '_{max_dist}m').format(dataset=dataset,
                                         n_months=n_months,
                                         max_dist=max_dist)
    #Check if table already exists in current schema
    #If not, create it
    if table_name not in tables_in_schema(con, current_schema):
        logger.info('Table {} does not exist... Creating it'.format(table_name))
        path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
                        'blight_risk_prediction',
                        'features',
                        template)
        #Load template with SQL statement
        with open(path_to_template, 'r') as f:
            sql_script = Template(f.read())
        #Replace values in template
        sql_script = sql_script.substitute(TABLE_NAME=table_name,
                                           DATASET=dataset,
                                           DATE_COLUMN=date_column,
                                           N_MONTHS=n_months,
                                           MAX_DIST=max_dist)
        #Run the code using the connection
        #this is going to take a while
        con.cursor().execute(sql_script)
        #Commit changes to db
        con.commit()
    else:
        logger.info('Table {} already exists. Skipping...'.format(table_name))

    cur.close()
    #Load data
    e = create_engine(uri)
    logger.info('Loading {} month table...'.format(table_name))
    if columns=='all':
        #Since the table contains a geom column, you need to subselect columns
        #to load otherwise pandas will complain
        cols = columns_for_table_in_schema(con, table_name, current_schema)
        valid_cols = filter(lambda x: x[1]!= 'USER-DEFINED', cols)
        cols_to_load = [x[0] for x in valid_cols]
    #If the user passed and array in the columns parameter, only
    #select those columns
    else:
        cols_to_load = columns

    df = pd.read_sql_table(table_name, e,
                            schema=current_schema,
                            columns=cols_to_load)
    return df


def load_inspections_address_nmonths_table(con, dataset, date_column,
                                           n_months, max_dist, columns):
    return load_nmonths_table_from_template(con, dataset, date_column,
                            n_months, max_dist,
                            'inspections_address_xmonths.template.sql',
                            columns)

def load_inspections_latlong_nmonths_table(con, dataset, date_column,
                                           n_months, max_dist, columns):
    return load_nmonths_table_from_template(con, dataset, date_column,
                            n_months, max_dist,
                            'inspections_latlong_xmonths.template.sql',
                            columns)

def group_and_count_from_db(con, dataset, n_months, max_dist):
    table_name = ('insp2{dataset}_{n_months}months'
                  '_{max_dist}m').format(dataset=dataset,
                                         n_months=n_months,
                                         max_dist=max_dist)
    q = ('SELECT parcel_id, inspection_date, COUNT(*) AS total '
         'FROM {} '
         'GROUP BY parcel_id, inspection_date;').format(table_name)
    df = pd.read_sql(q, con, index_col=['parcel_id', 'inspection_date'])
    return df


def compute_frequency_features(df, columns,
                               ids=['parcel_id', 'inspection_date'],
                               add_total=True):
    #Function assumes ids and columns are lists, if user sent
    #only one string, convert it to a list
    ids = [ids] if type(ids)==str else ids
    columns = [columns] if type(columns)==str else columns

    ids_series = [df[i] for i in ids]
    cols_series = [df[i] for i in columns]
    #Group by parcel_id and inspection_date. Make columns with counts
    #for some columns
    cross = pd.crosstab(ids_series, cols_series)
    #If add total, add column with rows sums
    cross['total'] = cross.sum(axis=1)
    return cross
