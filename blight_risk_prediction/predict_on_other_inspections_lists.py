import os
from sklearn.externals import joblib
from dstools.config import main
from pymongo import MongoClient
from bson.objectid import ObjectId
from dataset import get_features_for_inspections_in_schema

#Given a mongo_id from an experiment
#perform predictions using that model on other inspections lists
#e.g. using all parcels or field_test table for evaluating performance
EXPERIMENT_ID = '56cce46ae0f48cdf9c6a7369'
#Where to load list of inspections and features?
SCHEMA = 'features_field_test_31dec2014'

#Where to pickle models
path_to_pickles = os.path.join(os.environ['OUTPUT_FOLDER'], "pickles")

#load model from pickle file
model = joblib.load(os.path.join(path_to_pickles, EXPERIMENT_ID)) 

#Now load features that the model was trained on
client = MongoClient(main['logger']['uri'])
collection = client['models']['cincinnati']
#Convert string with date and time to datetime object
results = collection.find_one({"_id": ObjectId(EXPERIMENT_ID)})
#Get table_name,feature_name tuples
features = results['feature_mapping']
#Mongodb returns tuples as lists, but our loading method
#takes tuples as parameter
features = [tuple(feat) for feat in features]

#Now get your custom inspections list and make a dataset with the
#features the model was trained on
dataset = get_features_for_inspections_in_schema(SCHEMA,
    features)

#Impute... when modeling impute is done using the mean,
#but I shouldn't do that with this dataset...

#Scale features using original scaler...

#Predict
#model.predict()

#Dump predictions