import pandas as pd
from string import Template
import os
from sqlalchemy import create_engine
from lib_cinci.db import uri
from lib_cinci.config import load
import logging
import logging.config
import re
import logging
import logging.config
from lib_cinci.config import load
from lib_cinci.features import tables_in_schema, columns_for_table_in_schema
from psycopg2 import ProgrammingError, InternalError

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

def make_nmonths_table_from_template(con, dataset, date_column,
                                    min_insp_date, max_insp_date,
                                    n_months, max_dist,
                                    template, load=False,  columns='all'):
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
    if table_name not in tables_in_schema(current_schema):
        logger.info('Table {} does not exist... Creating it'.format(table_name))
        path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
                        'model',
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
                                           MAX_DIST=max_dist,
                                           MIN_INSP_DATE=min_insp_date,
                                           MAX_INSP_DATE=max_insp_date)
        #Run the code using the connection
        #this is going to take a while
        cur.execute(sql_script)
        #Commit changes to db
        con.commit()

        #If table created has a geom column which type USER DEFINED,
        #delete it, we don't need it here
        cols = columns_for_table_in_schema(table_name, current_schema)
        if ('geom', 'USER-DEFINED') in cols:
            #Important: this is not prouction ready since it's
            #vulnerable to SQL injection, I haven't found any solution
            #to dynamically pass table names as parameters in psycopg2
            #it seems like the only solution is to prevent SQL injection
            #in the code
            q = ('ALTER TABLE {} DROP COLUMN geom').format(table_name)
            cur.execute(q)
            con.commit()
            logger.info('Table {} has a PostGIS column, deleting...'.format(table_name))
    else:
        logger.info('Table {} already exists. Skipping...'.format(table_name))

    cur.close()
    #Load data
    e = create_engine(uri)
    logger.info('Loading {} month table...'.format(table_name))
    if columns=='all':
        #Since the table contains a geom column, you need to subselect columns
        #to load otherwise pandas will complain
        cols = columns_for_table_in_schema(table_name, current_schema)
        valid_cols = filter(lambda x: x[1]!= 'USER-DEFINED', cols)
        cols_to_load = [x[0] for x in valid_cols]
    #If the user passed and array in the columns parameter, only
    #select those columns
    else:
        cols_to_load = columns

    if load:
        df = pd.read_sql_table(table_name, e,
                            schema=current_schema,
                            columns=cols_to_load)
        return df


def make_inspections_address_nmonths_table(con, dataset, date_column,
                                           min_insp_date, max_insp_date,
                                           n_months, max_dist, load=False,
                                           columns='all'):
    return make_nmonths_table_from_template(con, dataset, date_column,
                            min_insp_date, max_insp_date,
                            n_months, max_dist,
                            'inspections_address_xmonths.template.sql',
                            load, columns)

def make_inspections_latlong_nmonths_table(con, dataset, date_column,
                                           min_insp_date, max_insp_date,
                                           n_months, max_dist, load=False,
                                           columns='all'):
    return make_nmonths_table_from_template(con, dataset, date_column,
                            min_insp_date, max_insp_date,
                            n_months, max_dist,
                            'inspections_latlong_xmonths.template.sql',
                            load, columns)

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

def load_colpivot(con):
    # add the colpivot function to our Postgres schema
    with open(os.path.join(os.environ['ROOT_FOLDER'], 
                'model','features', 'colpivot.sql'), 'r') as fin:
        query = fin.read()

    cur = con.cursor()
    cur.execute(query)
    con.commit()

def make_table_of_frequent_codes(con, col, intable, outtable, dropifexists=True,
        coalesceto="'missing'", rnum=15, to_other="'other'"):
    """ Make a table of codes and counts, so we can filter on them.
        If you don't want to coalesce missing codes to anything, pass
        coalescto="null". Note that strings must be double-quoted, as in 
        coaelsto's default argument ("'missing'").
        All levels that are not among the top rnum most frequent ones will
        be set to to_other (which also needs to double-quoted if it's a string).
    """

    cur = con.cursor()

    if dropifexists:
        query = "DROP TABLE IF EXISTS {outtable};".format(outtable=outtable)
        cur.execute(query)
        con.commit()

    # create a table of the most common types,
    # so we can limit the pivot later to them
    query = """
        CREATE TABLE {outtable} AS (
        WITH t as (
        SELECT coalesce({col},{coalesceto}) AS raw_level, count(*) AS count
        FROM {intable}
        GROUP BY {col}
        ORDER BY count desc
        )
        SELECT 
            row_number() OVER () as rnum,
            t.raw_level,
            CASE WHEN row_number() OVER () <= {rnum} THEN t.raw_level
            ELSE {to_other} END AS level
        FROM t
        );

    """.format(outtable=outtable, col=col, coalesceto=coalesceto,
                intable=intable, rnum=rnum, to_other=to_other)

    # if it already exists and hasn't been dropped above, don't re-run
    try:
        cur.execute(query)
        con.commit()
    except ProgrammingError as e:
        logger.warning("Catching Exception: " + e.message)
        logger.warning(" - CONTINUING, NOT RE-RUNNING {outtable} table QUERY.".format(
            outtable=outtable))
        con.rollback()
