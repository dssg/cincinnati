from lib_cinci.config import main
from psycopg2 import connect
from sqlalchemy import create_engine
from lib_cinci.db import uri
import pandas as pd
import re
import time
from dateutil.relativedelta import relativedelta

import logging
import logging.config
from lib_cinci.config import load

logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

#Parameters in some of these functions are being passed in SQL queries,
#this makes them vulverable to SQL injection, if this goes into production
#local SQL verification will be needed

def existing_feature_schemas():
    engine = create_engine(uri)
    schemas = "SELECT schema_name AS schema FROM information_schema.schemata"
    schemas = pd.read_sql(schemas, con=engine)["schema"]
    schemas = [s for s in schemas.values if s.startswith("features")]
    return schemas


def parse_feature_pattern(pattern):
    '''
    Parse feature pattern - based on a string with the format
    table.column, table.%, table.col_% find all columns matching
    Returns a tuple
    '''
    #print 'Parsing pattern: %s' % pattern
    table, column_pattern = pattern.split('.')
    query = ("SELECT table_name, column_name FROM information_schema.columns "
             "WHERE table_schema='features' AND table_name=%s AND "
             "column_name LIKE %s;")

    #Create psycopg2 connection object
    conn = connect(host=main['db']['host'], user=main['db']['user'],
                   password=main['db']['password'], database=main['db']['database'],
                   port=main['db']['port'])
    cur = conn.cursor()
    #Query db and get results
    cur.execute(query, (table, column_pattern))
    results = cur.fetchall()
    #Close connection
    cur.close()
    conn.close()
    return results

def parse_feature_pattern_list(patterns):
    '''
    Parses a list of patterns and returns a single list with tuples (table_name, feature_name)
    '''
    #Apply parsing method to each pattern
    features = [parse_feature_pattern(pattern) for pattern in patterns]
    #Flatten list
    features = [item for sublist in features for item in sublist]
    return features

def tables_and_columns_for_schema(schema):
    query = ("SELECT table_name, column_name FROM information_schema.columns "
             "WHERE table_schema=%s;")
    #Create psycopg2 connection object
    conn = connect(host=main['db']['host'], user=main['db']['user'],
                   password=main['db']['password'], database=main['db']['database'],
                   port=main['db']['port'])
    cur = conn.cursor()
    #Query db and get results
    cur.execute(query, (schema,))
    results = cur.fetchall()
    #Close connection
    cur.close()
    conn.close()
    return results

#Utility function to see which tables already exist in schema
def tables_in_schema(schema):
    q = '''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema=%s;
    '''
    con = connect(host=main['db']['host'], user=main['db']['user'],
                   password=main['db']['password'], database=main['db']['database'],
                   port=main['db']['port'])
    cur = con.cursor()
    cur.execute(q, [schema])
    tuples = cur.fetchall()
    names = [t[0] for t in tuples]
    cur.close()
    con.close()
    return names

def columns_for_table_in_schema(table, schema):
    q = '''
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s
        AND table_name   = %s;
    '''
    con = connect(host=main['db']['host'], user=main['db']['user'],
                   password=main['db']['password'], database=main['db']['database'],
                   port=main['db']['port'])
    cur = con.cursor()
    cur.execute(q, [schema, table])
    tuples = cur.fetchall()
    #names = [t[0] for t in tuples]
    cur.close()
    con.close()
    return tuples

def check_nas_threshold(df, threshold):
    nas_count = df.apply(pd.isnull).sum()
    nas_prop = nas_count/df.shape[0]
    above_threshold = nas_prop[nas_prop > threshold]
    if not above_threshold.empty:
        raise Exception(('The following columns have higher NAs proportion '
            'than allowed:\n{}'.format(above_threshold)))
    return nas_prop

def __check_element(element):
    pattern = re.compile('^(\w|\.)+$')
    result = pattern.match(element)
    if result is None:
        raise ValueError('"{}" is not a valid argument'.format(element))

def boundaries_for_table_and_column(table, column):
    __check_element(table)
    __check_element(column)

    db = create_engine(uri)

    q_min = 'SELECT MIN({}) FROM {}'.format(column, table)
    q_max = 'SELECT MAX({}) FROM {}'.format(column, table)

    min_val = db.execute(q_min).fetchone()[0]
    max_val = db.execute(q_max).fetchone()[0]

    return min_val, max_val


def check_date_boundaries(con, n_months, table, date_column):
    '''
        This function returns the min and max dates of inspections 
        for which you can generate features
    '''
    #Get current schema
    cur = con.cursor()    
    cur.execute('SELECT current_schema;')
    current_schema = cur.fetchone()[0]
    cur.close()

    #Get boundaries for current inspections table
    insp_table = '{}.parcels_inspections'.format(current_schema)
    min_insp, max_insp = boundaries_for_table_and_column(insp_table, 'inspection_date')

    #Get boundaries for features table
    min_feat, max_feat = boundaries_for_table_and_column(table, date_column)

    #Set inspections table subset to None
    lower_insp_subset = None
    upper_insp_subset = None

    #Check that you have data for the lowest boundary (min_insp - n_months)
    #if not, raise and exception since you don't have enough data to generate
    #features for those dates
    #Compare using time.mktime to avoid errors due to datetime.date with datetime.datetime
    #comparisons
    lowest_boundary = min_insp - relativedelta(months=n_months)
    if not time.mktime(min_feat.timetuple()) <= time.mktime(lowest_boundary.timetuple()):
        #Lower inspections table date: min_feat + n_months
        lower_insp_subset = min_feat + relativedelta(months=n_months)
        logging.info(('Warning: You cannot generate features for those dates, '
            'your first observation for table "{table}" is {min_feat} and the earliest date '
            'needed is {lowest_boundary} which is your earliest inspection ({min_insp}) minus n_months '
            '({n_months}). Inspections table will be subset starting from: '
            '{lower_insp_subset}').format(table=table, min_feat=min_feat, lowest_boundary=lowest_boundary,
            min_insp=min_insp, n_months=n_months, lower_insp_subset=lower_insp_subset))
    
    #Check that you have data for the highest boundary (max_insp)
    #if not, raise and exception since you don't have enough data to generate
    #features for those dates
    if not time.mktime(max_insp.timetuple()) <= time.mktime(max_feat.timetuple()):
        #Upper inspections table date: max_feat
        upper_insp_subset = max_feat
        logging.info(('Warning: You cannot generate features for those dates, '
            'your last observation for table "{table}" is {max_feat} and the '
            'latest inspection is {max_insp}. Inspections table will be subset '
            'ending in {upper_insp_subset}').format(table=table,
            max_feat=max_feat, max_insp=max_insp, upper_insp_subset=upper_insp_subset))

    #If lower_insp_subset or upper_insp_subset are still
    #none, set them to the min and max dates in the inspections table
    if lower_insp_subset is None:
        lower_insp_subset = min_insp
    if upper_insp_subset is None:
        upper_insp_subset = max_insp

    return '{:%Y-%m-%d}'.format(lower_insp_subset), '{:%Y-%m-%d}'.format(upper_insp_subset)
