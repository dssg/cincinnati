import pandas as pd
import numpy as np

import os
import fnmatch
import re

from sqlalchemy import create_engine
import yaml
import pymongo
from pymongo import MongoClient

from datetime import date, datetime
import dateutil
from dateutil import relativedelta

from lib_cinci.evaluation import (load_one_inspection_per_parcel, 
                                  add_latlong_to_df)

#enter where you are saving experiments
experiment_directory = os.path.join(os.getcwd(), 'medium_models')

#space_delta, time_delta
space_delta = '400m'
time_delta = '12months'

# where to save model results
results_filepath = 'model-results-' + str(date.today()) + '.csv'

# 5% of all parcels 
k = 7500

# validation schema
validation_feature_schema = 'features_31aug2016'

#setup database configuration and DB connection
from sklearn_evaluation.Logger import Logger
folder = os.environ['ROOT_FOLDER']
name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
main = yaml.load(text)

def load(name):
    folder = os.environ['ROOT_FOLDER']
    path = "%s/%s" % (folder, name)
    with open(path, 'r') as f:
        text = f.read()
    dic = yaml.load(text)
    return dic

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'.format(**connparams)
libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'.format(**connparams)

engine = create_engine(uri)
logger = Logger(host=main['logger']['uri'], db=main['logger']['db'], 
                collection=main['logger']['collection'])

# function to get the parameters from the yaml config file 
def get_config_parameters(experiment_config):
    with open(experiment_config, 'r') as f:
        df = pd.io.json.json_normalize(yaml.load(f))
        df.set_index('experiment_name', drop=False, inplace=True)
        return df

# get all experiment configs from the directory
experiment_configs = []
for root, dirnames, filenames in os.walk(experiment_directory):
    for filename in fnmatch.filter(filenames, '*.yaml'):
        experiment_configs.append(os.path.join(root, filename))

# get parameters and experiment names from all of these experiments
experiments = {experiment_config: get_config_parameters(experiment_config) 
                                  for experiment_config in experiment_configs}

#experiment_names = map(lambda v: v['experiment_name'][0], experiments.values())
experiment_names = map(lambda v: v['experiment_name'][0], experiments.values())[0:5]

# get all models for each experiment
all_models_by_experiment = [logger.get_all_from_experiment(exp_name) for exp_name in experiment_names]
all_models = [item for sublist in all_models_by_experiment for item in sublist]

for m in all_models:
    m['model_id'] = str(m['_id'])

#get neighborhood feature table 
neighborhood_table = 'neighborhood_score_' + space_delta + '_' + time_delta
neighborhood_history = pd.read_sql_table(neighborhood_table, engine,
                                         schema = validation_feature_schema,
                                         index_col = 'parcel_id')
neighborhood_history.drop('inspection_date', axis=1, inplace=True)

neighborhood_history['violations_per_house'] = neighborhood_history.unique_violations/neighborhood_history.houses
neighborhood_history['violations_per_inspection'] = neighborhood_history.unique_violations/neighborhood_history.unique_inspections
neighborhood_history['inspection_density'] = neighborhood_history.unique_inspections/neighborhood_history.houses

inspection_density_first_quartile = neighborhood_history['inspection_density'].quantile(0.25)
violations_per_house_first_quartile = neighborhood_history['violations_per_house'].quantile(0.25)
violations_per_inspection_first_quartile = neighborhood_history['violations_per_inspection'].quantile(0.25)

neighborhood_with_location = add_latlong_to_df(neighborhood_history[['violations_per_house', 
                                                                     'violations_per_inspection',
                                                                     'inspection_density']])
     
#get predictions on top k parcels for validation start date                                                                        
output_folder = os.environ['OUTPUT_FOLDER']
path_to_predictions = os.path.join(output_folder, 'top_predictions_on_all_parcels')

for model in all_models:
    # get validation start, end 
    test_start = re.split('_', model['experiment_name'])[2].lower()
    model['test_start'] = test_start

    validation_start = datetime.strptime(test_start, '%d%b%Y') + relativedelta.relativedelta(months=6)
    validation_end = validation_start + relativedelta.relativedelta(months=6) 
    
    # get saved scores
    model_top_k = pd.read_csv(os.path.join(path_to_predictions, model['model_id']), 
                              nrows=k+1, 
                              usecols=['parcel_id', 'prediction']) 
    
    # load inspection results from validation window 
    validation_inspections = load_one_inspection_per_parcel(validation_start, validation_end)
    validation_inspections.reset_index(inplace=True)
    
    # get intersection of this model's top k with parcels that were inspected
    # during validation window, and the results of those inspections
    top_k_inspected = validation_inspections[validation_inspections['parcel_id'].isin(model_top_k['parcel_id'])]
    
    # get validation precision and labeled percent
    model['validation_precision_at_p'] =  100.0*top_k_inspected.viol_outcome.sum()/top_k_inspected.shape[0]
    model['validation_labeled_percent'] = 100.0*(top_k_inspected.shape[0])/k

#save results to CSV
all_models_df = pd.DataFrame(all_models)
all_models_df.to_csv(results_filepath, index=False)

