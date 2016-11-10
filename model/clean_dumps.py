#!/usr/bin/env python
#This script cleans the MongoDB after running an experiment
#by keeping just the top 20 models
from pymongo import MongoClient
from pymongo import DESCENDING
from lib_cinci.config import main
from lib_cinci.config import load
from lib_cinci.folders import (path_to_predictions, path_to_pickled_models,
    path_to_pickled_scalers, path_to_pickled_imputers)
import os
import logging
import logging.config

'''
    Using the --pickle option in model.py will dump the
    model, scaler and imputer objects. Use this to only keep
    the top_n models from each experiment and delete the rest.
'''

#logger config
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

#Directories to check for files
directories = [path_to_predictions,
                path_to_pickled_models,
                path_to_pickled_scalers,
                path_to_pickled_imputers]

#db connection
client = MongoClient(main['logger']['uri'])
db = client['models']
collection = db['cincinnati']

#Top n models to keep from each experiment
n = 20

#Get experiments names
experiments = collection.distinct('experiment_name')

ids_to_keep = []
#For each experiment_name, sort by precision at 5% and
#keep n models, get the ids
for experiment_name in experiments:
    #Get the ids for the top models
    logger.info("Removing from experiment {}".format(experiment_name))
    object_ids = list(collection.find({"experiment_name": experiment_name}, {'_id':1})
        .sort("prec_at_5", DESCENDING)
        .limit(n))
    ids = [obj['_id'] for obj in object_ids]
    #Remove documents that match the experiment name and are not in the
    #top ids
    object_ids_to_del = collection.find({ '_id': { '$nin': ids }, 'experiment_name': experiment_name},
                        {'_id':1})
    ids_to_del = [obj['_id'] for obj in object_ids_to_del]
    result = collection.delete_many({ '_id': { '$in': ids_to_del }})
    logger.info("{} documents removed from MongoDB...".format(result.deleted_count))
    #add ids to keep to list
    ids_to_keep.extend(ids)


#Convert ids to a tuple of strings
ids_to_keep = tuple([str(an_id) for an_id in ids_to_keep])

#Delete all files in path that do not match any prefix in fields_to_keep
def delete_from_not_in(path, files_to_keep):
    '''
        Given a folder, removes all files that do not match
        any value in files_to_keep
    '''
    #Get a list of all files
    files = os.listdir(path)

    #Get list of files that do not start with any of ids_to_keep
    to_delete = [a_file for a_file in files if not a_file.startswith(ids_to_keep)]

    #Remove files
    for a_file in to_delete:
        os.remove(os.path.join(path, a_file))

    logger.info("Removed {} files from {}".format(len(to_delete), path))

#Apply function to every folder
for directory in directories:
    delete_from_not_in(directory, ids_to_keep)

