import pandas as pd
from dstools.db import uri
from sqlalchemy import create_engine
from string import Template

engine = create_engine(uri)

def create_events_3months_table(con):
    #Load template with SQL statement
    with open('events_xmonths.template.sql', 'r') as f:
        sql_script = Template(f.read())
    #Replace values in template
    sql_script = sql_script.substitute(TABLE_NAME='fire')
    #Run the code using the connection
    #this is going to take a while
    try:
        con.cursor().execute(sql_script)
    except Exception, e:
        print 'Failed to create 3 month table. {}'.format(e)

def compute_frequency_features(con):
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
    #Create table with events that happened before 3 months of inspection database
    #If table exists, send message and skip
    create_events_3months_table(con)

    #Use the recently created table to compute features.
    #Group rows by parcel_id and inspection_date
    #For now, just perform counts on the categorical variables
    #More complex features could combine the distance value
    #as well as interacting features
    df = compute_frequency_features(con)
    return df