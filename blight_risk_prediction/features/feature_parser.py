#This script contains functions to parse
#features specified in the configuration file
#for the modeling step
from dstools.config import main
from psycopg2 import connect


def parse_feature_pattern(pattern):
    '''
    Parse feature pattern - based on a string with the format
    table.column, table.%, table.col_% find all columns matching
    Returns a tuple
    '''
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
