import pandas as pd 
import numpy as np
from sklearn_evaluation.Logger import Logger
from sqlalchemy import create_engine
from lib_cinci.config import load
import os 
import yaml
import itertools

folder = os.environ['ROOT_FOLDER']
output_folder = os.environ['OUTPUT_FOLDER']
path_to_output = os.path.join(output_folder, 'model_groups.csv')

name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
main = yaml.load(text)
logger = Logger(host=main['logger']['uri'], 
                db=main['logger']['db'], 
                collection=main['logger']['collection'])

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'.format(**connparams)
libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'.\
                format(**connparams)

engine = create_engine(uri)

query = 'SELECT * FROM model_results.all_models;'
all_models = pd.read_sql(query, engine, index_col='model_id')
engine.dispose()

# add group number to all models
all_models['group_number'] = None
group_number = 1

for model in all_models.index.values:
    # only start a new group if this model is not already a group member 
    if all_models.loc[model, 'group_number'] is None:
        model_group = [str(model_id) for model_id in Logger.get_model_across_splits(logger, model)]
        model_group.append(model)

        for friend in model_group:
             all_models.loc[friend, 'group_number'] = group_number
        
        group_number += 1

all_models['model_id'] = all_models.index.values
all_models[['model_id','model_number','group_number']].\
    to_csv(path_to_output, index=False)
