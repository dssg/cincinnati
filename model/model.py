#!/usr/bin/env python
import pandas as pd
import datetime
from dateutil import relativedelta
import re
import yaml
import os
import logging
import logging.config
import copy
import random
import numpy as np
from pydoc import locate
from lib_cinci import dataset
import evaluation
from features import feature_parser
import argparse
from sklearn import preprocessing
from sklearn.externals import joblib
from sklearn_evaluation.Logger import Logger
from sklearn_evaluation.metrics import precision_at
from grid_generator import grid_from_class, _generate_grid

from lib_cinci.config import main as cfg_main
from lib_cinci.config import load
from lib_cinci.exceptions import MaxDateError, ConfigError, ExperimentExists
from lib_cinci.folders import (path_to_predictions, path_to_pickled_models,
                               path_to_pickled_scalers,
                               path_to_pickled_imputers,
                               path_to_dumps,
                               path_to_top_predictions_on_all_parcels)
from lib_cinci.features import (check_nas_threshold,
                                boundaries_for_table_and_column)

"""
Purpose: train a binary classifier to identify those homes that are likely
to have at least one violation.
"""

#NAs proportion threshold, when loading the training and test sets,
#the script will check the proportion of NAs and will raise an Exception
#when at least one column has a higher value than the threshold
NAS_PROPORTION_THRESHOLD = 0.5

logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

dirs = [path_to_predictions, path_to_pickled_models,
         path_to_pickled_scalers, path_to_pickled_imputers,
         path_to_dumps,
         path_to_top_predictions_on_all_parcels]
#Make directories if they don't exist
for directory in dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)

def configure_model(config_file):
    logger.info("Reading config from {}".format(config_file))
    with open(config_file, 'r') as f:
        cfg = yaml.load(f)

    if "start_date" not in cfg:
        cfg["start_date"] = '01Jan1970'

    if "residential_only" not in cfg:
        cfg["residential_only"] = False

    return cfg, copy.deepcopy(cfg)
    
def get_models_from_config(models_selected, grid_size):
    """
    Args:
        models_selected ([str]): List of models, as specified in the config YAML.
        grid_size (str): Grid size, as given in the config YAML.
    Returns ([dict]): List of models.
    """
    models = []
    for m in models_selected:
        # if the model is a dict, the user has supplied parameters,
        # over which we take the product
        if type(m) == dict:
            if len(m.keys()) > 1 or len(m.values()) > 1:
                raise ValueError("A model is not specified correctly.")
            modelclass = m.keys()[0]
            paramdicts = _generate_grid(m.values()[0])

            logging.info("%s has parameter ranges supplied; "
                         "ignoring grid_size"%modelclass)

            for paramdict in paramdicts:
                models.append(
                        locate(modelclass)(**paramdict)
                        )
        else:
            # just use the pre-specified grid-class
            for thism in grid_from_class(m, size=grid_size):
                models.append(thism)
    return models

def make_datasets(config, predictset=False):
    start_date = datetime.datetime.strptime(config["start_date"], '%d%b%Y')
    fake_today = datetime.datetime.strptime(config['fake_today'], '%d%b%Y')

    # parse the validation window
    dnum, units = re.match(r"(\d+)(\w+)", config["validation_window"]).groups() 
    if float(dnum)%1 != 0:
        raise ValueError("The validation window needs an integer!")
    dnum = int(dnum)
    units = units.lower()
    unitdict = {'month':'M', 'day':'D'}
    if units not in unitdict.keys():
        raise ValueError("Validation window units need to be 'Month' or 'Day'!")
    training_end = pd.date_range(start=fake_today, periods=2, 
                                 freq='%d%s'%(dnum,unitdict[units]))[1]

    #Before proceeding, make sure dates for training and testing are 
    #May 05, 2015 at most. Further dates won't work since you don't
    #have data.
    #Check start date
    
    _, max_date = boundaries_for_table_and_column('features.parcels_inspections',
        'inspection_date')
    
    if start_date > max_date:
        raise MaxDateError(('Error: Your start_date exceeds '
            '{:%B %d, %Y}, which is the latest inspection in '
            '"features.parcels_inspections" table').format(max_date))
    #Check fake today + validation window
    if training_end > max_date:
        raise MaxDateError('Error: your fake_today + validation_window exceeds '
             '{:%B %d, %Y}, which is the latest inspection in '
             '"features.parcels_inspections" table'.format(max_date))

    #Parse each feature pattern (table_name.pattern) in the config file and
    #return a list with tuples of the form (table_name, feature_name)
    features = feature_parser.parse_feature_pattern_list(config["features"])
    #print 'Selected features based on yaml file %s' % features

    only_residential = config["residential_only"]

    #Train set is built with a list of features, parsed from the configuration
    #file. Data is obtained between start date and fake today.
    #it is possible to select residential parcels only.
    #Data is obtained from features schema
    train = dataset.get_training_dataset(
        features=features,
        start_date=start_date,
        end_date=fake_today,
        only_residential=only_residential)

    #Test set is built in a similar way: list of features parsed from configuration
    #file, but the start date is just where out trainin set finishes and the end date
    #is the validation window. Residential flag also applies
    #Data is obtained from features schema
    test = dataset.get_testing_dataset(
        features=features,
        start_date=fake_today,
        end_date=training_end,
        only_residential=only_residential)

    if not predictset:
        return train, test
    else:
        schema = "features_{}".format(
                    (training_end) 
                        .strftime('%d%b%Y')).lower()
        preds = dataset.get_features_for_inspections_in_schema(
                schema=schema,
                features=features,
                only_residential=only_residential)

    return train, test, preds

def output_evaluation_statistics(test, predictions):
    logger.info("Statistics with probability cutoff at 0.5")
    # binary predictions with some cutoff for these evaluations
    cutoff = 0.5
    predictions_binary = np.copy(predictions)
    predictions_binary[predictions_binary >= cutoff] = 1
    predictions_binary[predictions_binary < cutoff] = 0

    evaluation.print_model_statistics(test.y, predictions_binary)
    evaluation.print_confusion_matrix(test.y, predictions_binary)

    precision1 = precision_at(test.y, predictions, 0.01)
    logger.debug("Precision at 1%: {} (probability cutoff {})".format(
                 round(precision1[0], 2), precision1[1]))
    precision10 = precision_at(test.y, predictions, 0.1)
    logger.debug("Precision at 10%: {} (probability cutoff {})".format(
                 round(precision10[0], 2), precision10[1]))
    #evaluation.plot_precision_at_varying_percent(test.y, predictions)

def get_feature_importances(model):
    try:
        return model.feature_importances_
    except:
        pass
    try:
        logging.info(('This model does not have feature_importances, '
                      'returning .coef_[0] instead.'))
        return model.coef_[0]
    except:
        logging.info(('This model does not have feature_importances, '
                      'nor coef_ returning None'))
    return None

def log_predictions_on_all(preds, predictions_on_all, mongo_id, topx):

    # Dump test_labels, test_predictions and test_parcels to a csv file
    parcel_id = [record[0] for record in preds.parcels]
    inspection_date = [record[1] for record in preds.parcels]
    dump = pd.DataFrame({'parcel_id': parcel_id,
                         'inspection_date': inspection_date,
                         'prediction': predictions_on_all})

    # restrict to top X most risky predictions
    dump = dump.sort_values(by='prediction', ascending=False)
    dump = dump.head(int( pd.np.round( len(dump)*topx/100. ) ) )

    # Dump predictions to CSV
    dump.to_csv(os.path.join(path_to_top_predictions_on_all_parcels, mongo_id))

def log_results(model, config, test, predictions, feature_importances,
                imputer, scaler):
    '''
        Log results to a MongoDB database
    '''
    # Instantiate logger
    logger_uri = cfg_main['logger']['uri']
    logger_db = cfg_main['logger']['db']
    logger_collection = cfg_main['logger']['collection']
    mongo_logger = Logger(logger_uri, logger_db, logger_collection)
    # Compute some statistics to log
    prec_at_1, cutoff_at_1 = precision_at(test.y, predictions, 0.01)
    prec_at_5, cutoff_at_5 = precision_at(test.y, predictions, 0.05)
    prec_at_10, cutoff_at_10 = precision_at(test.y, predictions, 0.1)
    prec_at_20, cutoff_at_20 = precision_at(test.y, predictions, 0.2)

    # Add the name of the experiment if available
    experiment_name = (config["experiment_name"] if config["experiment_name"]
                       else None)
    # Sending model will log model name, parameters and datetime
    # Also log other important things by sending named parameters

    ft_imp = list(feature_importances)
    ft_map = test.feature_mapping

    mongo_id = mongo_logger.log_model(model,
                                      config=config,
                                      prec_at_1=prec_at_1,
                                      cutoff_at_1=cutoff_at_1,
                                      prec_at_5=prec_at_5,
                                      cutoff_at_5=cutoff_at_5,
                                      prec_at_10=prec_at_10,
                                      cutoff_at_10=cutoff_at_10,
                                      prec_at_20=prec_at_20,
                                      cutoff_at_20=cutoff_at_20,
                                      experiment_name=experiment_name) #,
                                      # features=list(test.feature_names),
                                      # feature_mapping=ft_map,
                                      # feature_importances=ft_imp)


    # Dump test_labels, test_predictions and test_parcels to a csv file
    parcel_id = [record[0] for record in test.parcels]
    inspection_date = [record[1] for record in test.parcels]
    dump = pd.DataFrame({'parcel_id': parcel_id,
                         'inspection_date': inspection_date,
                         'viol_outcome': test.y,
                         'prediction': predictions})
    # Dump predictions to CSV
    dump.to_csv(os.path.join(path_to_predictions, mongo_id))
    # Pickle model
    if args.pickle:
        path_to_file = os.path.join(path_to_pickled_models, mongo_id)
        logger.info('Pickling model: {}'.format(path_to_file))
        joblib.dump(model, path_to_file)

        path_to_file = os.path.join(path_to_pickled_imputers, mongo_id)
        logger.info('Pickling imputer: {}'.format(path_to_file))
        joblib.dump(imputer, path_to_file)

        path_to_file = os.path.join(path_to_pickled_scalers, mongo_id)
        logger.info('Pickling scaler: {}'.format(path_to_file))
        joblib.dump(scaler, path_to_file)

    return mongo_id


def main():

    if args.warninglog:
        myhandler = logging.FileHandler(os.path.abspath(args.warninglog))
        myhandler.setLevel('WARNING')
        logger.addHandler(myhandler)
    if args.debuglog:
        myhandler2 = logging.FileHandler(os.path.abspath(args.debuglog))
        myhandler2.setLevel('DEBUG')
        logger.addHandler(myhandler2)

    config_file = args.path_to_config_file
    config, config_raw = configure_model(config_file)

    if args.predicttop and args.notlog:
        raise ValueError("You cannot save the top X predictions "
                "on all parcels without also logging.")

    #If logging is enabled, check that there are no records for
    #the selected experiment
    if not args.notlog:

        logger_uri = cfg_main['logger']['uri']
        logger_db = cfg_main['logger']['db']
        logger_collection = cfg_main['logger']['collection']
        mongo_logger = Logger(logger_uri, logger_db, logger_collection)

        if mongo_logger.experiment_exists(config['experiment_name']):

            # if the user hasn't selected to overwrite the record, throw error
            if not args.overwritelog:
                raise ExperimentExists(config['experiment_name'])
            else:
                mongo_logger.delete_experiment(config['experiment_name'])

    # datasets
    logger.info('Loading datasets...')
    if not args.predicttop:
        train, test  = make_datasets(config, predictset=False)
        logger.debug('Train x shape: {} Test x shape: {}'.format(train.x.shape,
            test.x.shape))
    else:
        train, test, preds = make_datasets(config, predictset=True)
        logger.debug('Train x shape: {} Test x shape: {} Prediction x shape {}'\
                .format(train.x.shape, test.x.shape, preds.x.shape))

    #Check percentage of NAs for every feature,
    #raise an error if at least one feature has more NAs than the
    #acceptable threshold
    logger.info('Checking training set NAs...')
    prop = check_nas_threshold(train.to_df(), NAS_PROPORTION_THRESHOLD)
    logger.debug(prop)
    logger.info('Checking testing set NAs...')
    prop = check_nas_threshold(test.to_df(), NAS_PROPORTION_THRESHOLD)
    logger.debug(prop)

    # Dump datasets if dump option was selected
    if args.dump:
        logger.info('Dumping train and tests sets')
        datasets = [(train, 'train'), 
                    (test, 'test')]
        if args.predicttop:
            logger.info('Dumping prediction sets')
            datasets.append((preds, 'prediction'))
        for data, name in datasets:
            if data is not None:
                filename = '{}_{}.csv'.format(config["experiment_name"], name)
                try:
                    #Try to convert to dataframe, it will fail if data is empty
                    df = data.to_df()
                except Exception, e:
                    logger.info('Error saving {} as csv: {}'.format(filename, e))
                finally:
                    df.to_csv(os.path.join(path_to_dumps, filename))
            else:
                logger.info('{} is None, skipping dump...'.format(name))

    #Impute missing values (mean is the only strategy for now)
    # Note that the features can specify imputation strategies;
    # and if they don't, then they already got a default imputer,
    # which imputes the median (for floats), or 0 (for integers)
    logger.info('Imputing values on train and test...')
    imputer = preprocessing.Imputer().fit(train.x)
    train.x = imputer.transform(train.x)
    test.x = imputer.transform(test.x)
    logger.debug('Train x shape: {} Test x shape: {}'.format(train.x.shape,
        test.x.shape))
    if args.predicttop:
        preds.x = imputer.transform(preds.x)
        logger.debug('Prediction x shape: {}'.format(preds.x.shape))

    # Scale features to zero mean and unit variance
    logger.info('Scaling train, test...')
    scaler = preprocessing.StandardScaler().fit(train.x)
    train.x = scaler.transform(train.x)
    test.x = scaler.transform(test.x)
    logger.debug('Train x shape: {} Test x shape: {}'.format(train.x.shape,
        test.x.shape))
    if args.predicttop:
        preds.x = scaler.transform(preds.x)
        logger.debug('Prediction x shape: {}'.format(preds.x.shape))

    #Get size of grids
    grid_size = config["grid_size"]
    #Get list of models selected
    models_selected = config["models"]

    models = get_models_from_config(models_selected, grid_size)

    if args.shufflemodels:
        random.shuffle(models)

    # fit each model for all of these
    for idx, model in enumerate(models):
        #Try to run in parallel if possible
        if hasattr(model, 'n_jobs'):
            model.set_params(n_jobs=args.n_jobs)

        #SVC does not predict probabilities by default
        if hasattr(model, 'probability'):
            model.probability = True

        timestamp = datetime.datetime.now().isoformat()

        # train
        logger.info("{} out of {} - Training {}".format(idx+1,
                                                        len(models),
                                                        model))
        model.fit(train.x, train.y)

        # predict
        logger.info("Predicting on validation samples...")
        predicted = model.predict_proba(test.x)
        predicted = predicted[:, 1]  # probability that label is 1

        # statistics
        output_evaluation_statistics(test, predicted)
        feature_importances = get_feature_importances(model)

        # predict on all parcels, if selected
        if args.predicttop:
            predicted_on_all = model.predict_proba(preds.x)[:,1]
            # rank by risk, only keep the top X %

        # save results
        prefix = config["experiment_name"] if config["experiment_name"] else ''
        config_raw["parameters"] = model.get_params()
        
        #Log depending on user selection
        if args.notlog:
            logger.info("You selected not to log results. Skipping...")
        else:
            #Log parameters and metrics to MongoDB
            #Save predictions to CSV file
            #and pickle model
            model_id = log_results(model, config_raw, test, predicted,
                feature_importances, imputer, scaler)
            if args.predicttop:
                log_predictions_on_all(preds, predicted_on_all, 
                                       model_id, float(args.predicttop))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--path_to_config_file",
                        help=("Path to the yaml configuration file. "
                              "Defaults to the default.yaml in the $ROOT_FOLDER"),
                        type=str, default=os.path.join(os.environ["ROOT_FOLDER"], "default.yaml"))
    parser.add_argument("-n", "--n_jobs", type=int, default=-1,
                            help=("n_jobs flag passed to scikit-learn models, "
                                  "fails silently if the model does not support "
                                  "such flag. Defaults to -1 (all jobs possible)"))
    parser.add_argument("-nl", "--notlog", action="store_true",
                        help="Do not log results to MongoDB")
    parser.add_argument("-ol", "--overwritelog", action="store_true",
                        help="If the experiment already exists "
                        "in the MongoDB, overwrite it.")
    parser.add_argument("-p", "--pickle", action="store_true",
                        help="Pickle model, imputer and scaler, "
                        "only valid if logging is activated")
    parser.add_argument("-d", "--dump", action="store_true",
                        help=("Dump train and test sets (including indexes), "
                              "before imputation and scaling. "
                              "Output will be saved as "
                              "$OUTPUT_FOLDER/dumps/[experiment_name]_[train/test]"))
    parser.add_argument("-pt", "--predicttop", type=int, default=None,
                        help="Make predictions on all parcels, and "
                        "store the top X percent. Will be saved to "
                        "$OUTPUT_FOLDER/dumps/[experiment_name]_predict. " 
                        "Requires that the corresponding features have been created.")
    parser.add_argument("-sm", "--shufflemodels", action="store_true",
                        help="Shuffle the order in which models are being run.")
    parser.add_argument("-wl", "--warninglog", type=str, default=None,
                        help="Specify a filepath to a log file for "
                        "warnings. Does not affect the standard pipeline logging.")
    parser.add_argument("-dl", "--debuglog", type=str, default=None,
                        help="Specify a filepath to a log file for "
                        "debug info. Does not affect the standard pipeline logging.")
    args = parser.parse_args()
    main()

