from lib_cinci.config import main
from psycopg2 import connect
from sqlalchemy import create_engine
from lib_cinci.db import uri
import pandas as pd
import re

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
    pattern = re.compile('^\w+$')
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
