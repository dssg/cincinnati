from pymongo import MongoClient
from utils import get_model_name
import datetime
import pymongo
from bson.objectid import ObjectId

def _flatten_dict(mydict, joinfunc=lambda a,b: '.'.join([a,b])):
    """
    Helper function to take a dictionary and flatten it. Key-value pairs
    in nested dicts are being translated to top-level key-value pairs, where
    the nested keys are joined.
    For example, {'aa': 11, 'cc': {'aaa': 111, 'bbb': 222}, 'bb': 22} becomes
    {'aa': 11, 'bb': 22, 'cc.aaa': 111, 'cc.bbb': 222}.
    Args:
        mydict (dict): Dictionary to be flattened.
        joinfunc (func): A function that takes to keys and returns
                         one key. By default, string joining with '.'
    Returns (dict): The flattened dict.
    """

    for k in mydict.keys():
        if '.' in k:
            raise ValueError(("There is a '.' in %s. This will cause "
                "problems, as '.' is part of the MongoDB search syntax.")%k)

    simple_dict = {k:v for k,v in mydict.iteritems()
                    if type(v)!=dict}

    # if the dict is flat, return it
    if len(simple_dict)==len(mydict):
        return simple_dict

    to_flatten = {k:v for k,v in mydict.iteritems()
                    if type(v)==dict}

    # recursively unpack all values that are dicts,
    # rename the keys by concating the name with parent keys
    flattened = {joinfunc(k,kk):vv
                 for k,v in to_flatten.iteritems()
                 for kk,vv in _flatten_dict(v,joinfunc).iteritems()
                }

    simple_dict.update(flattened)
    return simple_dict


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

    def get_all_from_experiment(self, experiment_name):
        '''
           Returns all models from one experiment
        '''
        models = self.collection.find({"experiment_name": experiment_name})
        n_models = models.count() 
        return ( list(models[:]))

    def delete_experiment(self, experiment_name):
        ''' 
            Delete an experiment by key
        '''
        to_delete = [c['_id'] for c in 
                self.collection.find({'experiment_name': experiment_name})]
        self.collection.delete_many({ '_id': { '$in': to_delete }})

    def get_model_across_splits(self, model_id):
        """
        Finds the IDs of all models that have been trained with the same config
        and sklearn parameters as model_id, but that have been trained on a 
        different temporal split than model_id.
        Args:
            model_id (str): The MongoDB ID for a single (sklearn) models.
        Returns ([ObjectId]): A list of MongoDB IDs, corresponding to all models 
                        that have identical YAML configs and sklearn paramters as 
                        model_id, except for their start_date and fake_today.
                        However, the returned list only includes models for which 
                        the distance between start_date and fake_today is the same
                        as for model_id.
        """

        # fetch the document for this model_id
        model_cfg = list(self.collection.find({'_id':ObjectId(model_id)}))
        if len(model_cfg) > 1:
            raise ValueError("There is more than one model config for '%s'!"%model_id)
        else:
            model_cfg = model_cfg[0]

        # we will match documents by 'name' (the sklearn model name),
        # 'parameters' (the sklearn model parameters), and 'config' (the YAML),
        # *except* 'start_date' and 'fake_today', and 'experiment_name' 
        # in the YAML
        start_date = datetime.datetime.strptime(
                model_cfg['config'].pop('start_date'), '%d%b%Y')
        fake_today = datetime.datetime.strptime(
                model_cfg['config'].pop('fake_today'), '%d%b%Y')
        train_len = fake_today - start_date
        experiment_name = model_cfg['config'].pop('experiment_name')

        # we want all documents that are identical in a subset of 
        # the fields
        match_keys = ['name','parameters','config'] 

        # translate the nested documents to Mongo's dot-syntax
        searchdict = _flatten_dict({k: model_cfg[k] for k in match_keys})

        # get all the documents that match (but not model_id's one)
        res = self.collection.find({
                    '$and': [searchdict,
                             {'_id': {'$ne': ObjectId(model_id)}}
                            ] })

        # now toss those out where the training interval has the wrong length
        res_ids = []
        for r in res:
            this_start_date = datetime.datetime.strptime(r['config']['start_date'],
                                                         '%d%b%Y')
            this_fake_today = datetime.datetime.strptime(r['config']['fake_today'],
                                                         '%d%b%Y')

            if (this_fake_today - this_start_date) == train_len:
                res_ids.append(r['_id'])

        return res_ids

    def get_doc_from_id(self, model_id):
        """ Fetch the document for a given model_id """

        model_cfg = list(self.collection.find({'_id':ObjectId(model_id)}))
        if len(model_cfg) > 1:
            raise ValueError("There is more than one model config for '%s'!"%model_id)

        return model_cfg[0]

