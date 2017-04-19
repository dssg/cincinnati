import pandas as pd 
from sqlalchemy import create_engine
import os
import yaml
from lib_cinci.config import load


folder = os.environ['ROOT_FOLDER']
output_folder = os.environ['OUTPUT_FOLDER']

path_to_output = os.path.join(output_folder, 'feature_crosstabs.csv')

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'.format(**connparams)
engine = create_engine(uri)

validation_schema = 'features_31aug2016'

# get all tables from feature schema, excluding
# 'insp2' tables (they are lookups, not features),
# named_entities and parcels_inspections
query = '''
        SELECT DISTINCT table_name 
        FROM information_schema.tables
        WHERE table_schema = '{schema}'
        AND SUBSTRING(table_name FROM 1 FOR 5) != 'insp2'
        AND table_name NOT IN ('parc_year', 'parcels_inspections', 
                               'named_entities');
        '''.format(schema=validation_schema)

all_tables = pd.read_sql(query, engine)
all_features = {}

for table in all_tables.table_name.values:
    column_query = '''
              SELECT DISTINCT column_name 
              FROM information_schema.columns
              WHERE table_schema = '{schema}'
              AND table_name = '{table}' 
              AND column_name != 'parcel_id'
              AND column_name != 'inspection_date'
              AND data_type IN ('double precision', 'bigint', 'integer');
              '''.format(schema=validation_schema, table=table)
    
    columns = pd.read_sql(column_query, engine)
    column_names = list(columns.column_name.values)

    model_query = 'SELECT model_group, subset, ' 
    all_query = '''SELECT 1 as model_group, 'All Parcels' as subset,'''
    
    if len(column_names) > 1:    
        for col in list(columns.column_name.values)[:-1]:
            model_query += 'AVG("{col}") AS "{table}_{col}", '.format(table=table, col=col)
            all_query += 'AVG("{col}") AS "{table}_{col}", '.format(table=table, col=col)

        model_query += '''
                        AVG ("{col}") AS "{table}_{col}"
                        FROM model_results.all_top_k top_k
                        JOIN {schema}.{table} t
                        ON top_k.parcel_id = t.parcel_id
                        GROUP BY model_group, subset;
                       '''.format(schema=validation_schema, 
                                  col=column_names[-1], 
                                  table=table)

        all_query += '''
                        AVG ("{col}") AS "{table}_{col}" 
                        FROM {schema}.{table} 
                        GROUP BY model_group, subset;
                      '''.format(schema=validation_schema,
                                 col=column_names[-1], 
                                 table=table)
    
    elif len(column_names) == 1:
         model_query = '''
                       SELECT model_group,
                       subset, 
                       AVG("{col}") AS "{table}_{col}" 
                       FROM model_results.all_top_k top_k
                       JOIN {schema}.{table} t
                       ON top_k.parcel_id = t.parcel_id 
                       GROUP BY model_group, subset;
                       '''.format(schema=validation_schema, col=column_names[0], table=table)
         
         all_query = '''
                     SELECT 1 AS model_group, 
                     'All Parcels' as subset,
                     AVG("{col}") AS "{table}_{col}"
                     FROM {schema}.{table} 
                     GROUP BY model_group, subset;
                     '''.format(schema=validation_schema, col=column_names[0], table=table)

    elif len(column_names) == 0:
        continue

    average_top_five = pd.read_sql(model_query, engine, index_col = ['model_group', 'subset'])
    average_all_parcels = pd.read_sql(all_query, engine, index_col = ['model_group', 'subset'])
    engine.dispose()

    all_features[table] = pd.concat([average_top_five, average_all_parcels],
                                     keys=['Model Top 5% Average', 'All Parcel Average'], 
                                     names=['quantity'])

ct = pd.concat(all_features.values(), axis=1)
ct.reset_index(inplace=True)
all_crosstabs = pd.melt(ct, id_vars=['model_group','quantity','subset'], var_name ='feature')
all_crosstabs.to_csv(path_to_output, index=False)
