import pandas as pd 
from sqlalchemy import create_engine
import os
import yaml
from lib_cinci.config import load

folder = os.environ['ROOT_FOLDER']
name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
main = yaml.load(text)

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'.format(**connparams)
libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'.format(**connparams)

engine = create_engine(uri)

# get all tables from feature schema, excluding
# 'insp2' tables - they are lookups, not features
query = '''
        SELECT DISTINCT table_name 
        FROM information_schema.tables
        WHERE table_schema = 'features_31aug2016'
        AND SUBSTRING(table_name FROM 1 FOR 5) != 'insp2';
        '''

all_tables = pd.read_sql(query, engine)
all_features = {}

## FOR MODEL FEATURE AVERAGES
for table in all_tables.table_name.values[0:2]:
    column_query = '''
              SELECT DISTINCT column_name 
              FROM information_schema.columns
              WHERE table_schema = 'features_31aug2016'
              AND table_name = '{table}' 
              AND column_name != 'parcel_id'
              AND column_name != 'inspection_date'
              AND data_type IN ('double precision', 'bigint', 'integer');
              '''.format(table=table)
    columns = pd.read_sql(column_query, engine)

    model_query = 'SELECT model_number, ' 
    all_query = 'SELECT 1 as model_number, '

    for col in list(columns.column_name.values)[:-1]:
        model_query += 'AVG({col}) AS {table}_{col}, '.format(table=table, col=col)
        all_query += 'AVG({col}) AS {table}_{col}, '.format(table=table, col=col)

    model_query += '''
        AVG ({col}) AS {table}_{col}
        FROM all_top_five 
        JOIN features_31aug2016.{table} t
        ON all_top_five.parcel_id = t.parcel_id
        GROUP BY model_number
        '''.format(col=columns.column_name.values[-1], table=table)

    all_query += 'AVG ({col}) AS {table}_{col} FROM features_31aug2016.{table} GROUP BY model_number;'.format(col=columns.column_name.values[-1], table=table)
        
    average_top_five = pd.read_sql(model_query, engine, index_col = 'model_number')
    average_top_five['table_name'] = table
    average_top_five['group'] = 'all parcel average'
    
    average_all_parcels = pd.read_sql(all_query, engine, index_col = 'model_number')
    average_all_parcels['table_name'] = table
    average_all_parcels['group'] = 'top k average' 

    all_features[table] = pd.concat([average_all_parcels, average_top_five])
pd.concat(all_features.values()).to_csv('feature_crosstabs_test.csv')
