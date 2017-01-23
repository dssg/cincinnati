"""
Given a model_id, train a model with this model_id's configuration and 
parameters, but using all data up to a different end-of-training ('fake_today')
date. Then, use this model to predict the outcome for all datapoints in a given 
prediction_schema. Return the trained model and the predictions.
"""

from sklearn_evaluation.Logger import Logger
from lib_cinci.config import main as cfg
from lib_cinci import dataset
from lib_cinci.features import parse_feature_pattern_list
from lib_cinci.exceptions import ConfigError
import datetime
from sklearn import preprocessing
from pydoc import locate
import os
import argparse
import logging
import logging.config
from lib_cinci.config import load
import pandas as pd
import pickle

logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def get_config(model_id):
    """ Give a model_id (string or ObjectId), return the entire MongoDB log
        for that model.
    """

    logger = Logger(host=cfg['logger']['uri'],
                    db=cfg['logger']['db'],
                    collection=cfg['logger']['collection'])

    logging.info("Fetched model_id %s."%str(model_id))

    return logger.get_doc_from_id(model_id)


def train_on_config(myconfig, n_jobs=-1):
    """
    Using a configuration dictionary (like the ones that are stored in 
    the MongoDB), train a model with the corresponding selection of data, 
    features, parameters, etc.
    Args:
        myconfig (dict): A configuration dictionary, as it would be returned
                         from the MongoDB.
        n_jobs (int): Gets passed to scikit-learn and limits the number of 
                      cores that it runs on.
    Returns:
        model (sklearn model): The fitted sklearn model.
        imputer (sklearn imputer): The fitted sklearn imputer.
        scaler (sklearn scaler): The fitted sklearn scaler.
        features (list): The parsed list of features from the config file.
        column_names (list): The training data's column names
    """
    
    # parse the configuration dictionary 
    features = parse_feature_pattern_list(myconfig["config"]["features"])
    start_date = datetime.datetime.strptime(myconfig["config"]["start_date"], '%d%b%Y')
    fake_today = datetime.datetime.strptime(myconfig["config"]['fake_today'], '%d%b%Y')
    only_residential = myconfig["config"]["residential_only"]

    logging.info("Length of feature list: %s"%str(len(features)))
    logging.info("Fetching training data from %s to %s."%(str(start_date),
                                                          str(fake_today)))

    # fetch the training data, using the dates from the config dict
    train = dataset.get_training_dataset(
        features=features,
        start_date=start_date,
        end_date=fake_today,
        only_residential=only_residential)

    column_names = train.x.columns.tolist()

    logging.info("Size of training dataset: %s"%str(train.x.shape))

    # fit the imputer and scaler
    imputer = preprocessing.Imputer().fit(train.x)
    train.x = imputer.transform(train.x)
    scaler = preprocessing.StandardScaler().fit(train.x)
    train.x = scaler.transform(train.x)

    # Here comes a hack: in the MongoDB, we only store e.g.
    # 'RandomForestClassifier'; but we need 
    # 'sklearn.ensemble.RandomForestClassifier'. Fortunately, the longer names
    # are stored in myconfig['config']['models'].
    modelclasses = [x for x in myconfig['config']['models']
                    if x.endswith(myconfig['name'])]
    if len(modelclasses) > 1:
        raise ValueError('Failed to uniquely identify model %s'%myconfig['name'])

    # fit the model
    modelclass = modelclasses[0]
    model = locate(modelclass)(**myconfig['config']['parameters'])

    logging.info("Selected algorithm: %s"%str(model))

    if hasattr(model, 'n_jobs'):
        model.set_params(n_jobs=n_jobs)

    # SVC does not predict probabilities by default
    if hasattr(model, 'probability'):
        model.probability = True
    
    logging.info("Starting sklearn fitting...")
    model.fit(train.x, train.y)
    logging.info("Finished sklearn fitting.")

    return model, imputer, scaler, features, column_names


def predict_on_date(prediction_schema, model, imputer, scaler, features, return_features=False):
    """
    Given a fitted set of imputer, scaler, and model, and a list of features
    that the model needs, make predictions for all parcels, using the data
    from one of the prediction schemas (where the input features are calculated
    up to some chosen date).
    Args:
        prediction_schema (str): Name of a schema in the Postgres DB, like
                                 'features_31aug2016'. This data will be used
                                 for making predictions.
        model (sklearn model): Fitted sklearn model.
        imputer (sklearn imputer): Fitted sklearn imputer.
        scaler (sklearn scaler): Fitted sklearn scaler.
        features (list): List of features for the above model.
        return_features (bool): If True, then the returned dataframe also
                                contains all the features. If False, it only
                                contains the predictions.
    Returns (pd.DataFrame):
        DataFrame, indexed by parcel_id, that gives a prediction for each parcel;
        if return_features==True, it also gives all the feature columns (un-imputed,
        un-scaled).
    """

    # fetch the features from the prediction_schema
    dset = dataset.get_features_for_inspections_in_schema(prediction_schema, features)

    logging.info("Size of prediction dataset: %s."%str(dset.x.shape))

    # remember the un-imputed, un-scaled features
    raw_df = dset.to_df()

    # apply the learned sklearn model
    col_names = dset.x.columns
    dset.x = imputer.transform(dset.x)
    dset.x = scaler.transform(dset.x)
    preds_proba = model.predict_proba(dset.x)[:, 1]

    # get the column names back, as dset.x is now a np.array
    dset.x = pd.DataFrame(dset.x, columns=col_names)

    # clean up the dataframe of raw features
    raw_df['prediction'] = preds_proba
    raw_df = raw_df.reset_index().drop(['inspection_date','viol_outcome'],1)
    raw_df = raw_df.set_index('parcel_id')

    if return_features:
        return raw_df

    return raw_df[['prediction']]


def main(model_id, train_end_date, prediction_schema, n_jobs=-1, 
        return_features=False, return_fitted=False):
    """
    Args:
        model_id (str or ObjectId): ID of model to re-train
        train_end_date (str): Like '30Jun2016'. Labels up to this date will be
                              used to train the model.
        prediction_schema (str): Name of a schema in the Postgres DB, like
                                 'features_31aug2016'. This data will be used
                                 for making predictions. The schema must have 
                                 been run.
        n_jobs (int): Maximum number of cores sklearn is allowed to use.
        return_features (bool): If this flag is selected, returns a df with the 
                                full feature matrix, not just the predictions. 
        return_fitted (bool): If this flag is selected, a second return value 
                              is provided: a dictionary with keys 'model', 
                              'imputer', and 'scaler', giving the corresponding,
                              fitted sklearn objects.
    Returns (pd.DataFrame):
        DataFrame, indexed by parcel_id, that gives a prediction for each parcel;
        if return_features==True, it also gives all the feature columns (un-imputed,
        un-scaled)
        if return_fitted==True, also gives a dictionary of fitted sklearn objects.
    """

    myconfig = get_config(model_id)

    # drop everything we don't want from the config
    myconfig = {x:myconfig[x] for x in ['name','parameters','config']}
    del myconfig['config']['experiment_name']

    # shift the dates
    start_date = datetime.datetime.strptime(myconfig['config']['start_date'], 
                                            '%d%b%Y')
    fake_today = datetime.datetime.strptime(myconfig['config']['fake_today'], 
                                            '%d%b%Y')
    train_len = fake_today - start_date

    logging.info("Config start date: %s"%str(start_date))
    logging.info("Config fake_today: %s"%str(fake_today))
    logging.info("Training window length: %s."%str(train_len))

    new_fake_today = datetime.datetime.strptime(train_end_date, '%d%b%Y')
    new_start_date = new_fake_today - train_len

    logging.info("Shifted start date: %s"%str(new_start_date))
    logging.info("Shifted fake_today: %s"%str(new_fake_today))
    logging.info("Shifted training window length: %s."%str(
                                new_fake_today-new_start_date))

    # now update the config
    myconfig['config']['start_date'] = datetime.datetime.strftime(new_start_date,
                                                                  '%d%b%Y')
    myconfig['config']['fake_today'] = datetime.datetime.strftime(new_fake_today,
                                                                  '%d%b%Y')

    # train the model
    model, imputer, scaler, features, column_names = train_on_config(myconfig, n_jobs)

    # predict on new date
    res_df = predict_on_date(prediction_schema,model,imputer,scaler,features,return_features) 

    res_column_names = res_df.columns.tolist()
    res_column_names.remove('prediction')

    if res_column_names != column_names:
        raise ConfigError("The columns between the training and the prediction "
                           "don't match.")

    if not return_fitted:
        return res_df

    return res_df, {'model':model, 'imputer':imputer, 'scaler':scaler}

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-mid", "--model_id",
                        help=("MongoDB ID string for the model that you'd like to "
                              "fit and use for prediction."), type=str)
    parser.add_argument("-ed", "--train_end_date",
                        help=("String, like '30Jun2016', which marks the end of "
                              "the training data."), type=str)
    parser.add_argument("-ps", "--prediction_schema",
                        help=("String, like 'features_31aug2016', giving the name "
                              "of the schema from which the features for prediction "
                              "will be drawn."), type=str)
    parser.add_argument("-n", "--n_jobs", type=int, default=-1,
                            help=("n_jobs flag passed to scikit-learn models, "
                                  "fails silently if the model does not support "
                                  "such flag. Defaults to -1 (all jobs possible)"))
    parser.add_argument("-o", "--outfile",
                        help=("Path to the CSV file which contains "
                              "the predictions. Defaults to "
                              "$ROOT_FOLDER/field_test_preparation/predictions.csv"),
                        type=str, default=os.path.join(os.environ["ROOT_FOLDER"], 
                            "field_test_preparation","predictions.csv"))
    parser.add_argument("-rf", "--return_features", action="store_true",
                        help="If this flag is selected, the dump includes the "
                        "full feature matrix (un-imputed, un-scaled), "
                        "not just the predictions.", default=False)
    parser.add_argument("-psp", "--pickle_sklearn_path",
                        help=("Optional path to folder for fitted sklearn imputer, "
                            "scaler, and model. If given, a folder with that name "
                            "will be created, and corresponding pickle dumps saved "
                            "in it."),
                        type=str, default=None)
    args = parser.parse_args()

    dump_sklearn = True if args.pickle_sklearn_path else False

    res = main(args.model_id, args.train_end_date, args.prediction_schema, 
                       args.n_jobs, args.return_features, dump_sklearn)

    if dump_sklearn:
        df, fitted = res
    else:
        df = res

    if args.outfile:
        with open(args.outfile,'w') as fout:
            df.to_csv(fout, index=True)

    if dump_sklearn:
        os.makedirs(args.pickle_sklearn_path)
        for k,v in fitted.iteritems():
            with open(os.path.join(args.pickle_sklearn_path, k+'.p'),'w') as fout:
                pickle.dump(v, fout)

