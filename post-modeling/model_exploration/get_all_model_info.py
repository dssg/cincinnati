import pandas as pd
import numpy as np
import os
import sys
import fnmatch
import re
from sqlalchemy import create_engine
import yaml
from datetime import date, datetime
import dateutil
from dateutil.relativedelta import relativedelta
from lib_cinci.evaluation import load_one_inspection_per_parcel 
from lib_cinci.config import load, get_config_parameters 
from sklearn_evaluation.metrics import precision_at
from sklearn_evaluation.Logger import Logger
import ast
import itertools

#directory location of experiment configs
experiment_directory = sys.argv[0]

#space and time windows for neighborhood history
space_delta = '400m'
time_delta = '12months'

# where to save model results and where to get predictions
output_folder = os.environ['OUTPUT_FOLDER']
path_to_output = os.path.join(output_folder, 'all_models.csv')
path_to_predictions = os.path.join(output_folder, 'top_predictions_on_all_parcels')

# k - number of parcels to use for precision and neighborhood metrics
k = 7500

# validation schema
validation_feature_schema = 'features_31aug2016'
validation_months = 6

#setup database configuration and DB connection
folder = os.environ['ROOT_FOLDER']
name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
main = yaml.load(text)

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'.format(**connparams)
#libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'.format(**connparams)

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

for model in all_models:
    # get validation start date, end date 
    test_start = re.split('_', model['experiment_name'])[2].lower()
    model['test_start'] = test_start

    validation_start = datetime.strptime(test_start, '%d%b%Y') + relativedelta(months=validation_months)
    validation_end = validation_start + relativedelta(months=validation_months) 
    
    # get saved scores
    model_top_k = pd.read_csv(os.path.join(path_to_predictions, model['model_id']), 
                              nrows=k,
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
                                                       ignore_nas=True)[0] # not all parcels in top k will have inspections
    model['validation_labeled_percent'] = 100.0*(top_k_inspected.viol_outcome.notnull().sum())/k

all_models_df = pd.DataFrame(all_models)
all_models_df.set_index('model_id', inplace=True)

#turn config dict into columns in the all models dataframe
config_dict = all_models_df['config'].map(str).apply(ast.literal_eval)
config_df = pd.DataFrame(config_dict.to_dict()).T
config_df.drop(['models', 'residential_only', 'parameters'], axis=1, inplace=True)

#calculate trainining window (length between train start and test start)
config_df['fake_today'] = config_df['fake_today'].apply(lambda x: datetime.strptime(x, '%d%b%Y'))
config_df['start_date'] = config_df['start_date'].apply(lambda x: datetime.strptime(x, '%d%b%Y'))
config_df['training_window'] = (config_df['fake_today'] - config_df['start_date']).astype('timedelta64[M]').map(int).map(str) + ' Months' 

param_dict = all_models_df['parameters'].map(str).apply(ast.literal_eval)
param_df = pd.DataFrame(param_dict.to_dict()).T

all_models = all_models_df.drop(['parameters', 'experiment_name', 'config'], axis=1)
all_models = all_models.join(config_df)
all_models = all_models.join(param_df)

all_models.drop(['_id', 'cutoff_at_1', 'cutoff_at_10', 'cutoff_at_20',
       'cutoff_at_5', 'datetime', 'fake_today'], 
                axis=1, inplace=True)

all_models['model_number'] = all_models.test_start.map({'31dec2013': 1,
                                                        '30jun2014': 2,
                                                        '31dec2014': 3,
                                                        '30jun2015': 4,
                                                        '31dec2015': 5})

all_models.to_csv(path_to_output)

