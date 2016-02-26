import os
from sklearn.externals import joblib
from lib_cinci.config import main
from pymongo import MongoClient
from bson.objectid import ObjectId
from dataset import get_features_for_inspections_in_schema
import pandas as pd

def predict_on_schema(model_id, schema):
    '''
        Use the model from a previous experiment to predict on one of the
        existing feature schemas.

        The function unpickles the model, scaler and imputer. Then, gets
        the features the model was trained on from MongoDB, loads the features
        from the PostgresSQL schema and predicts.

        For pickles to exist, use the --pickle option in model.py

        Example:
        model_id = '56ccea5ae0f48ce44f618afe'
        schema = 'features_field_test_31dec2014'
        df = predict_on_schema(model_id, schema)
    '''
    path_to_pickled_models = os.path.join(os.environ['OUTPUT_FOLDER'], "pickled_models")
    path_to_pickled_scalers = os.path.join(os.environ['OUTPUT_FOLDER'], "pickled_scalers")
    path_to_pickled_imputers = os.path.join(os.environ['OUTPUT_FOLDER'], "pickled_imputers")
    
    #load model from pickle file
    model = joblib.load(os.path.join(path_to_pickled_models, model_id)) 
    #load scaler
    scaler = joblib.load(os.path.join(path_to_pickled_scalers, model_id)) 
    #load imputer
    imputer = joblib.load(os.path.join(path_to_pickled_imputers, model_id)) 
    
    #Now load features that the model was trained on
    client = MongoClient(main['logger']['uri'])
    collection = client['models']['cincinnati']
    #Convert string with date and time to datetime object
    results = collection.find_one({"_id": ObjectId(model_id)})
    #Get table_name,feature_name tuples
    features = results['feature_mapping']
    #Mongodb returns tuples as lists, but our loading method
    #takes tuples as parameter
    features = [tuple(feat) for feat in features]
    
    #Now get your custom inspections list and make a dataset with the
    #features the model was trained on
    dataset = get_features_for_inspections_in_schema(schema, features)

    #Impute
    dataset.x = imputer.transform(dataset.x)
    #Scale
    dataset.x = scaler.transform(dataset.x)
    #Predict
    preds_proba = model.predict_proba(dataset.x)[:, 1]
    #Return a dataframe with parcel_id, inspection_date, viol_outcome and preds
    df = dataset.to_df()[['viol_outcome']]
    df['prediction'] = preds_proba
    return df