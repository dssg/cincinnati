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

from lib_cinci.config import load, get_config_parameters 

from sklearn_evaluation.metrics import precision_at

import ast
import itertools

#directory location of experiment configs
experiment_directory = os.path.join(os.getcwd(), 'medium_models')

#space and time windows for neighborhood history
space_delta = '400m'
time_delta = '12months'

# where to save model results
results_filepath = 'model-results-' + str(date.today()) + '.csv'

# k - number of parcels to use for precision and neighborhood metrics
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

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'.format(**connparams)
libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'.format(**connparams)

engine = create_engine(uri)
logger = Logger(host=main['logger']['uri'], db=main['logger']['db'], 
                collection=main['logger']['collection'])

# get all experiment configs from the directory
experiment_configs = []
for root, dirnames, filenames in os.walk(experiment_directory):
    for filename in fnmatch.filter(filenames, '*.yaml'):
        experiment_configs.append(os.path.join(root, filename))

# get parameters and experiment names from all of these experiments
experiments = {experiment_config: get_config_parameters(experiment_config) 
                                  for experiment_config in experiment_configs}

experiment_names = map(lambda v: v['experiment_name'][0], experiments.values())

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
violations_per_house_first_quartile = neighborhood_history['violations_per_house'].quantile(0.25)

neighborhood_history['inspection_density'] = neighborhood_history.unique_inspections/neighborhood_history.houses
inspection_density_first_quartile = neighborhood_history['inspection_density'].quantile(0.25)
     
#get saved model predictions as of validation date
output_folder = os.environ['OUTPUT_FOLDER']
path_to_predictions = os.path.join(output_folder, 'top_predictions_on_all_parcels')

i=1
for model in all_models:
    # get validation start, end 
    test_start = re.split('_', model['experiment_name'])[2].lower()
    model['test_start'] = test_start

    validation_start = datetime.strptime(test_start, '%d%b%Y') + relativedelta.relativedelta(months=6)
    validation_end = validation_start + relativedelta.relativedelta(months=6) 
    
    # get saved scores
    model_top_k = pd.read_csv(os.path.join(path_to_predictions, model['model_id']), 
                              nrows=k+1,
                              index_col='parcel_id',
                              usecols=['parcel_id','prediction']) 
    
    # load inspection results from validation window 
    validation_inspections = load_one_inspection_per_parcel(validation_start, validation_end)
    
    # get intersection of this model's top k with parcels that were inspected
    # during validation window, and the results of those inspections
    top_k_inspected = model_top_k.join(validation_inspections)
    
    # get validation precision and labeled percent
    model['validation_precision_at_p'] =  precision_at(top_k_inspected.viol_outcome,
                                                       model_top_k.prediction,
                                                       percent=1.0, # precision is calculated on top k, so use 100%
                                                       ignore_nas=True) # not all parcels in top k will have inspections
    model['validation_labeled_percent'] = 100.0*(top_k_inspected.shape[0])/k

    # add neighborhood info - mean and std dev of inspection density and violations per house 
    # on top k parcels for this model

    top_k_neighborhood = model_top_k.join(neighborhood_history)

    model['top_5_inspection_density_mean'] = top_k_neighborhood['inspection_density'].mean()
    model['top_5_inspection_density_std_dev'] = top_k_neighborhood['inspection_density'].std()
    model['top_5_low_inspection_density_percent'] = (top_k_neighborhood['inspection_density'] < inspection_density_first_quartile).mean()

    model['top_5_violations_per_house_mean'] = top_k_neighborhood['violations_per_house'].mean()
    model['top_5_violations_per_house_std_dev'] = top_k_neighborhood['violations_per_house'].std()
    model['top_5_low_violations_per_house_percent'] = (top_k_neighborhood['violations_per_house'] < violations_per_house_first_quartile).mean()

    print "finished model {0} of {1}".format(i, len(all_models))
    i+=1

#save results to CSV
all_models_df = pd.DataFrame(all_models)
config_dict = all_models_df['config'].map(str).apply(ast.literal_eval)
config_df = pd.DataFrame(config_dict.to_dict()).T
config_df.to_csv('configs.csv')
all_models_df.to_csv(results_filepath, index=False)

