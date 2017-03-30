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
# 'insp2' tables (they are lookups, not features),
# named_entities and parcels_inspections
query = '''
        SELECT DISTINCT table_name 
        FROM information_schema.tables
        WHERE table_schema = 'features_31aug2016'
        AND SUBSTRING(table_name FROM 1 FOR 5) != 'insp2'
        AND table_name NOT IN ('parc_year', 'parcels_inspections', 'named_entities');
        '''

all_tables = pd.read_sql(query, engine)
all_features = {}

for table in all_tables.table_name.values:
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
    column_names = list(columns.column_name.values)

    model_query = 'SELECT model_number, ' 
    all_query = 'SELECT 1 as model_number, '
    
    if len(column_names) > 1:    
        for col in list(columns.column_name.values)[:-1]:
            model_query += 'AVG("{col}") AS "{table}_{col}", '.format(table=table, col=col)
            all_query += 'AVG("{col}") AS "{table}_{col}", '.format(table=table, col=col)

        model_query += '''
                        AVG ("{col}") AS "{table}_{col}"
                        FROM all_top_five 
                        JOIN features_31aug2016.{table} t
                        ON all_top_five.parcel_id = t.parcel_id
                        GROUP BY model_number;
                       '''.format(col=column_names[-1], table=table)

        all_query += '''
                        AVG ("{col}") AS "{table}_{col}" 
                        FROM features_31aug2016.{table} 
                        GROUP BY model_number;
                      '''.format(col=column_names[-1], table=table)
    
    elif len(column_names) == 1:
         model_query = '''
                       SELECT model_number, AVG("{col}") AS "{table}_{col}" 
                       FROM all_top_five 
                       JOIN features_31aug2016.{table} t
                       ON all_top_five.parcel_id = t.parcel_id 
                       GROUP BY model_number
                       '''.format(col=column_names[0], table=table)
         
         all_query = '''
                     SELECT 1 AS model_number, AVG("{col}") AS "{table}_{col}"
                     FROM features_31aug2016.{table} 
                     GROUP BY model_number;
                     '''.format(col=column_names[0], table=table)

    elif len(column_names) == 0:
        continue

    average_top_five = pd.read_sql(model_query, engine, index_col = 'model_number')
    average_all_parcels = pd.read_sql(all_query, engine, index_col = 'model_number')
    ratio_top_five_to_all = average_top_five.divide(average_all_parcels.loc[1], axis=1)

    all_features[table] = pd.concat([average_top_five, average_all_parcels, ratio_top_five_to_all],
                                     keys=['Model Top 5% Average', 'All Parcel Average', 'Ratio'],
                                     names=['value'])

all_crosstabs = pd.concat(all_features.values(), axis=1)
all_crosstabs.reset_index(inplace=True)
all_crosstabs.sort_values('model_number').T.to_csv('feature_crosstabs.csv', header=False)

