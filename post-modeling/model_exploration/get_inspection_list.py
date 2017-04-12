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

model_id = '53454'

query = '''
        SELECT * 
        FROM model_results.all_top_k
        LEFT JOIN model_results.parcel_info
        USING parcel_id
        WHERE top_k.model_group = '{}'
        '''.format(model_id=model_id)

model_list = pd.read_sql(query, engine, index_col='parcel_id')
model_list.to_csv('inspection_list.csv')
