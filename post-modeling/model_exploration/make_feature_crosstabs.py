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
        SELECT DISTINCT (table_name) 
        FROM information_schema.tables
        WHERE table_schema = 'features_31aug2016'
        AND SUBSTRING(table_name FROM 1 FOR 5) != 'insp2';
        '''

all_tables = pd.read_sql(query, engine)
all_features = {}

for t in list(all_tables.table_name):
    query = 'SELECT * FROM features_31aug2016.{table};'.format(table=t)
    features = pd.read_sql(query, engine, index_col = 'parcel_id')
    if 'inspection_date' in features.columns:
        features.drop('inspection_date', axis=1, inplace=True)
    features.columns = [t + '.' + str(col) for col in features.columns]
    all_features[t] = features 

#combine all features
all_features_df = pd.concat(all_features.values())

#get mean over all parcels
all_features_mean = all_features_df.mean(axis=0)
print(all_features_mean.head())
#add a column for model group 
all_features_mean = all_features_mean.append(pd.Series([1.0]), index=['model_group']).to_frame().T
#all_features_mean_df = all_features_mean.to_frame().T

#get features averages on top 5% for each model
feature_average = {}

for m in model_groups:                                                   
    list_name = str(m)
    # change this to get top k from all_top5
    model_features = all_features[all_features.index.isin(top_k[list_name].index)].mean(axis=0)
    model_features = model_features.to_frame().T

    feature_averages[list_name + ' Top 5'] = model_features
    feature_averages[list_name + ' Top 5']['model_group'] = list_name
    feature_averages[list_name + ' Top 5']['subset'] = 'Top 5 Average'
    feature_averages[list_name + ' Top 5']['list'] = 'All Parcels'

    feature_averages[list_name + ' Ratio'] = model_features.divide(all_features_mean_df, axis=1)
    feature_averages[list_name + ' Ratio']['model_group'] = list_name
    feature_averages[list_name + ' Ratio']['subset'] = 'Ratio'
    feature_averages[list_name + ' Ratio']['list'] = 'All Parcels'

crosstabs = pd.concat(feature_averages.values())
crosstabs = crosstabs.append(all_features_mean_df)
crosstabs.set_index(['model_group','list','subset'], inplace=True)
crosstabs.reset_index(inplace=True)
crosstabs['new_index'] = crosstabs['model_group'].map(int).map(str) + ' ' + crosstabs['list'] + ' ' + crosstabs['subset']
crosstabs.set_index('new_index', inplace=True)
crosstabs.T.to_csv('feature_crosstabs.csv')
