import pandas as pd
from string import Template
import os
import re

#This file provides generic functions
#to generate spatiotemporal features

#Utility function to see which tables already exist in schema
def tables_in_schema(con, schema):
    q = '''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema={};
    '''.format(schema)
    cur = con.cursor()
    cur.execute(q)
    return cur.fetchall()


def create_inspections_address_xmonths_table(con, schema, table_name, date_column, n_months=3):
    path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
                    'blight_risk_prediction',
                    'features',
                    'inspections_address_xmonths.template.sql')
    #Load template with SQL statement
    with open(path_to_template, 'r') as f:
        sql_script = Template(f.read())
    #Replace values in template
    sql_script = sql_script.substitute(TABLE_NAME=table_name,
                                       DATE_COLUMN=date_column,
                                       N_MONTHS=n_months)
    #Run the code using the connection
    #this is going to take a while
    try:
        con.cursor().execute(sql_script)
    except Exception, e:
        con.rollback()
        con.cursor().execute("SET SCHEMA '{}'".format(schema))
        print 'Failed to create {} month table. {}'.format(n_months, e)

def create_inspections_latlong_xmonths_table(con, schema, table_name, date_column, n_months=3):
    path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
                    'blight_risk_prediction',
                    'features',
                    'inspections_latlong_xmonths.template.sql')
    #Load template with SQL statement
    with open(path_to_template, 'r') as f:
        sql_script = Template(f.read())
    #Replace values in template
    sql_script = sql_script.substitute(TABLE_NAME=table_name,
                                       DATE_COLUMN=date_column,
                                       N_MONTHS=n_months)
    #Run the code using the connection
    #this is going to take a while
    try:
        con.cursor().execute(sql_script)
    except Exception, e:
        con.rollback()
        con.cursor().execute("SET SCHEMA '{}'".format(schema))
        print 'Failed to create {} month table. {}'.format(n_months, e)

def compute_frequency_features(con, table_name, columns,
                               ids=['parcel_id', 'inspection_date'],
                               add_total=True):
    #Function assumes ids and columns are lists, if user sent
    #only one string, convert it to a list
    ids = [ids] if type(ids)==str else ids
    columns = [columns] if type(columns)==str else columns

    print 'Loading data from {}, computing frequency features'.format(table_name)

    df = pd.read_sql('SELECT * FROM {} LIMIT 100'.format(table_name), con)
    print 'Data loaded: %s' % df.head()
    ids_series = [df[i] for i in ids]
    cols_series = [df[i] for i in columns]
    #Group by parcel_id and inspection_date. Make columns with counts
    #for some columns
    cross = pd.crosstab(ids_series, cols_series)
    #If add total, add column with rows sums
    cross['total'] = cross.sum(axis=1)
    #tables are named SOMETHING_DATASET, get DATASET from table_name
    dataset = re.compile('^.+_{1}(\w+)$').findall(table_name)[0]
    #Rename columns to avoid capital letters and spaces
    #Add prefix to identify where this feature came from
    def process_column_name(raw_name):
        col_name = raw_name.replace(' ', '_').lower()
        return '{dataset}_{col_name}'.format(dataset=dataset, col=col_name)

    cross.columns = cross.columns.map(process_column_name)

    return cross
