import pandas as pd
from dstools.db import uri
from sqlalchemy import create_engine
from string import Template
import os

engine = create_engine(uri)

path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
                    'blight_risk_prediction',
                    'features',
                    'events_xmonths.template.sql')
table_name = 'fire'
date_column = 'date'

def create_events_3months_table(con, schema):
    #Load template with SQL statement
    with open(path_to_template, 'r') as f:
        sql_script = Template(f.read())
    #Replace values in template
    sql_script = sql_script.substitute(TABLE_NAME=table_name, DATE_COLUMN=date_column)
    #Run the code using the connection
    #this is going to take a while
    try:
        con.cursor().execute(sql_script)
    except Exception, e:
        con.rollback()
        con.cursor().execute("SET SCHEMA '{}'".format(schema))
        print 'Failed to create 3 month table. {}'.format(e)

def compute_frequency_features(con, schema):
    df = pd.read_sql('SELECT * FROM events_3months_fire', con)
    #Group by parcel_id and inspection_date. Make columns with counts
    #for some columns
    cross = pd.crosstab([df.parcel_id, df.inspection_date],
                         df.signal)
    #Rename columns to avoid capital letters and spaces
    cross.columns = cross.columns.map(lambda s: s.replace(' ', '_').lower())
    return cross

def make_fire_features(con):
    """
    Make Fire features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    #Save current schema, this is important because if some of the queries
    #fail, you need to do a rollback, which will reset the previously set schema
    cur = con.cursor()
    cur.execute('SELECT current_schema;')
    schema = cur.fetchone()

    #Create table with events that happened before 3 months of inspection database
    #If table exists, send message and skip
    create_events_3months_table(con, schema)

    #Use the recently created table to compute features.
    #Group rows by parcel_id and inspection_date
    #For now, just perform counts on the categorical variables
    #More complex features could combine the distance value
    #as well as interacting features
    df = compute_frequency_features(con, schema)
    return df
