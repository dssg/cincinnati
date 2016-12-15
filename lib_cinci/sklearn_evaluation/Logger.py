from pymongo import MongoClient
from utils import get_model_name
import datetime
import pymongo

class Logger:
    def __init__(self, host, db, collection):
        client = MongoClient(host)
        self.collection = client[db][collection]

    def log_model(self, model, **keywords):
        '''
            Log a model to the database
        '''
        params = model.get_params()
        name = get_model_name(model)
        dt = datetime.datetime.utcnow() 
        model = {'name': name, 'parameters': params, 'datetime': dt}
        for mym in keywords['config']['models']:
            if type(mym) == dict:
                old_key = mym.keys()[0]
                new_key = old_key.replace('.','_')
                mym[new_key] = mym.pop(old_key)
        model.update(keywords)
        inserted_id = self.collection.insert_one(model).inserted_id
        return str(inserted_id)

    def experiment_exists(self, experiment_name):
        '''
            Check if an experiment already exists
        '''
        model = {'experiment_name':experiment_name}
        model_count = self.collection.find(model).count()
        return model_count > 0

    def get_best_from_experiment(self, experiment_name, key):
        '''
            Returns entry for the best model given an experiment_name
            and a key
        '''
        return (self.collection.find({"experiment_name": experiment_name})
                    .sort(key, pymongo.DESCENDING)[0])

    def delete_experiment(self, experiment_name):
        ''' 
            Delete an experiment by key
        '''
        to_delete = [c['_id'] for c in 
                self.collection.find({'experiment_name': experiment_name})]
        self.collection.delete_many({ '_id': { '$in': to_delete }})

