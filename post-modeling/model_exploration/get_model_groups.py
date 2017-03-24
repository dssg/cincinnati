import pandas as pd 
import numpy as np
from sklearn_evaluation.Logger import Logger
import os 
import yaml

folder = os.environ['ROOT_FOLDER']
name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
main = yaml.load(text)
logger = Logger(host=main['logger']['uri'], 
                db=main['logger']['db'], 
                collection=main['logger']['collection'])

all_models = pd.read_csv('model-results-2017-03-23.csv', index_col='_id')

# make columns for model number and group number
all_models['model_number'] = all_models.test_start.map({'31dec2013': 1,
                                                        '30jun2014': 2,
                                                        '31dec2014': 3,
                                                        '30jun2015': 4,
                                                        '31dec2015': 5})
all_models['group_number'] = np.nan
group_number = 1

for model in all_models.index.values:

    if np.isnan(all_models.loc[model, 'group_number']):
        model_group = [str(model_id) for model_id in Logger.get_model_across_splits(logger, model)]
        model_group.append(model)

        for friend in model_group:
             all_models.loc[friend, 'group_number'] = group_number
        
        group_number += 1


all_models.to_csv('model-results-grouped.csv')

