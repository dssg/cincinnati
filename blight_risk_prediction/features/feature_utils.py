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
logger = logging.getLogger(__name__)

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

def load_nmonths_table_from_template(con, dataset, date_column, n_months, template):
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
    table_name = 'insp_{n_months}months_{dataset}'.format(n_months=n_months,
                                                          dataset=dataset)
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
        sql_script = sql_script.substitute(DATASET=dataset,
                                           DATE_COLUMN=date_column,
                                           N_MONTHS=n_months)
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
    logger.info('Loading {} month table...'.format(n_months))
    return pd.read_sql_table(table_name, e, schema=current_schema)


def load_inspections_address_nmonths_table(con, dataset, date_column, n_months=3):
    return load_nmonths_table_from_template(con, dataset,
                                            date_column,
                                            n_months,
                                            template='inspections_address_xmonths.template.sql')

def load_inspections_latlong_nmonths_table(con, dataset, date_column, n_months=3):
    return load_nmonths_table_from_template(con, dataset,
                                            date_column,
                                            n_months,
                                            template='inspections_latlong_xmonths.template.sql')


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
