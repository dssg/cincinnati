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
libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'.format(**\
connparams)

engine = create_engine(uri)

model_id = '53454 Below Median ID'
all_top_five = pd.read_csv('all_top5.csv', index_col=0)
predictions = all_top_five.loc[model_id]
predictions.reset_index(inplace=True)
predictions.set_index('parcel_id', inplace=True)

path_to_postprocess = os.path.join(os.environ['OUTPUT_FOLDER'], 'postprocess')
path_to_parcel_info = os.path.join(path_to_postprocess, 'parcel_info.csv')
parcel_info = pd.read_csv(path_to_parcel_info, index_col='parcel_id', 
                          usecols=['residential', 'address', 'tract', 'parcel_id'])

query = 'SELECT parcel_id, unique_inspections,unique_violations, houses FROM features_31aug2016.neighborhood_score_400m_12months;'
neighborhood_info = pd.read_sql(query, engine, index_col='parcel_id')

model_list = predictions.join(parcel_info).join(neighborhood_info)
model_list.to_csv('inspection_list.csv')
