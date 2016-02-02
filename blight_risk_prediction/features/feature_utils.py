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
        WHERE table_schema=%s;
    '''
    cur = con.cursor()
    cur.execute(q, [schema])
    tuples = cur.fetchall()
    names = [t[0] for t in tuples]
    return names


def load_inspections_address_nmonths_table(con, dataset, date_column, n_months=3):
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
        path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
                        'blight_risk_prediction',
                        'features',
                        'inspections_address_xmonths.template.sql')
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
    else:
        print 'Table {} already exists. Skipping...'.format(table_name)

    cur.close()
    #Load data
    df = pd.read_sql('SELECT * FROM %(table)s LIMIT 100', cons,
                     params={'table': table_name})
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
    #tables are named SOMETHING_DATASET, get DATASET from table_name
    dataset = re.compile('^.+_{1}(\w+)$').findall(from_table)[0]
    #Rename columns to avoid capital letters and spaces
    #Add prefix to identify where this feature came from
    def process_column_name(raw_name):
        col_name = raw_name.replace(' ', '_').lower()
        return '{dataset}_{col_name}'.format(dataset=dataset, col=col_name)

    cross.columns = cross.columns.map(process_column_name)
    return cross
