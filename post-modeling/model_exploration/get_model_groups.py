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
logger = Logger(host=main['logger']['uri'], db=main['logger']['db'], collection=main['logger']['collection'])

all_models = pd.read_csv('model-results-2017-03-23.csv', index_col='_id')

group_number = 1
model_number = 0

all_models['group_number'] = np.nan
all_models['model_number'] = all_models.test_start.apply(hash)
#model_groups = {}

for model in all_models.index.values:
    model_number += 1

    if np.isnan(all_models.loc[model, 'group_number']):
#        print "model number {0}".format(model_number)
        model_group = [str(model_id) for model_id in Logger.get_model_across_splits(logger, model)]
        model_group.append(model)
        model_groups[group_number] = model_group

        for friend in model_group:
             all_models.loc[friend, 'group_number'] = group_number
        
        group_number += 1

# all_models.set_index(['group_number', 'model_number']
#suffix = ['_model_1', '_model_2', '_model_3', '_model_4', '_model_5']
#list_index = list(itertools.product(models_with_info_unstacked.columns.get_level_values(0).unique(), suffix))
#ind = list([e[0] + e[1] for e in list_index])
#models_with_info_unstacked.columns = ind          
#models_with_info_unstacked = models_with_info_unstacked.rename(columns = {'MODELID_model_1': 'model_id_model_1', 
 #                 'MODELID_model_2': 'model_id_model_2', 
 #                  'MODELID_model_3': 'model_id_model_3',
 #                  'MODELID_model_4': 'model_id_model_4',
 #                  'MODELID_model_5': 'model_id_model_5',
 #                         'experiment_name_x_model_1': 'experiment_name_model_1',
 #                         'experiment_name_x_model_2': 'experiment_name_model_2',
 #                         'experiment_name_x_model_3': 'experiment_name_model_3',
 #                        'experiment_name_x_model_4': 'experiment_name_model_4',
 #                        'experiment_name_x_model_5': 'experiment_name_model_5'})


#filter_col = [col for col in list(models_with_info_unstacked) if col.startswith('experiment_name_y')]
#models_with_info_unstacked.drop(filter_col, axis=1, inplace=True)
all_models.to_csv('model-results-grouped.csv')
#pd.DataFrame.from_dict(model_groups, orient='index').to_csv('model_groups.csv')
