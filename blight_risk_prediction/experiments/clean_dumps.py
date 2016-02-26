from pymongo import MongoClient
from lib_cinci.config import main
from lib_cinci.folders import (path_to_predictions, path_to_pickled_models,
    path_to_pickled_scalers, path_to_pickled_imputers, path_to_dumps)

'''
    Using the --pickle option in model.py will dump the
    model, scaler and imputer objects. Use this to only keep
    the top_n models from each experiment and trash the rest.
'''

#db connection
client = MongoClient(main['logger']['uri'])
db = client['models']
collection = db['cincinnati']

#Top n models to keep from each experiment
n = 20

#For each experiment_name, sort by precision at 1% and
#keep n models, get the ids


#Use those ids to delete from
#pickled_imputers, pickled_models, pickled_scalers and predictions
#folders