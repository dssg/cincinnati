#!/usr/bin/env python
import matplotlib as mpl
mpl.use('Agg')
import pandas as pd
import datetime
import yaml
import pickle
import sys
import os
import logging
import copy
from itertools import product
import numpy as np
from sklearn import linear_model, preprocessing, svm, ensemble
from blight_risk_prediction import dataset, evaluation

from dstools.config import main as cfg_main
from sklearn_evaluation.Logger import Logger
from grid_generator import grid_from_class

"""
Purpose: train a binary classifier to identify those homes that are likely
to have at least one violation.
"""

logger = logging.getLogger(__name__)

#Name of the folder that will store rsults and predictions
#This folders are relative to $OUTPUT_FOLDER
results_dir = "results/"
predictions_dir = "predictions/"

#Max cores to use if possible
MAX_CORES = 4

class ConfigError():
    pass


def configure_model(config_file):
    logger.info("Reading config from {}".format(config_file))
    with open(config_file, 'r') as f:
        cfg = yaml.load(f)

    if "start_date" not in cfg:
        cfg["start_date"] = '01Jan1970'

    if "residential_only" not in cfg:
        cfg["residential_only"] = False

    # predict parcels
    if "prepare_field_test" in cfg:
        if "prepare_field_test" not in cfg:
            errmsg = "Set an inspection date to generate parcels to inspect"
            raise ConfigError(errmsg)
    else:
        cfg["prepare_field_test"] = False

    return cfg, copy.deepcopy(cfg)


def make_datasets(config):

    start_date = datetime.datetime.strptime(config["start_date"], '%d%b%Y')
    fake_today = datetime.datetime.strptime(config['fake_today'], '%d%b%Y')

    if config["validation_window"] == "1Year":
        validation_window = datetime.timedelta(days=365)
    elif config["validation_window"] == "1Month":
        validation_window = datetime.timedelta(days=30)
    else:
        raise ConfigError("Unsupported validation window: {}".format(
                          config["validation_window"]))

    features = [feat for feat, include in config["features"].items()
                if include]

    only_residential = config["residential_only"]

    train = dataset.get_training_dataset(
        features=features,
        start_date=start_date,
        end_date=fake_today,
        only_residential=only_residential)

    test = dataset.get_testing_dataset(
        features=features,
        start_date=fake_today,
        end_date=fake_today + validation_window,
        only_residential=only_residential)

    # Scale features to zero mean and unit variance
    scaler = preprocessing.StandardScaler().fit(train.x)
    train.x = scaler.transform(train.x)
    test.x = scaler.transform(test.x)

    field_train, field_test = None, None

    if config["prepare_field_test"]:
        inspection_date = datetime.datetime.strptime(config["inspection_date"],
                                                     '%d%b%Y')
        field_train = dataset.get_training_dataset(
            features=features,
            start_date=start_date,
            end_date=inspection_date,
            only_residential=only_residential)

        field_test = dataset.get_field_testing_dataset(
            features=features,
            fake_inspection_date=inspection_date,
            only_residential=only_residential)

        scaler = preprocessing.StandardScaler().fit(field_train.x)
        field_train.x = scaler.transform(field_train.x)
        field_test.x = scaler.transform(field_test.x)

    return train, test, field_train, field_test

def output_evaluation_statistics(test, predictions):

    logger.info("Statistics with probability cutoff at 0.5")

    # binary predictions with some cutoff for these evaluations
    cutoff = 0.5
    predictions_binary = np.copy(predictions)
    predictions_binary[predictions_binary >= cutoff] = 1
    predictions_binary[predictions_binary < cutoff] = 0

    evaluation.print_model_statistics(test.y, predictions_binary)
    evaluation.print_confusion_matrix(test.y, predictions_binary)

    precision1 = evaluation.precision_at_x_percent(test.y, predictions,
                                                   x_percent=0.01)
    logger.debug("Precision at 1%: {} (probability cutoff {})".format(
                 round(precision1[1], 2), precision1[0]))
    precision10 = evaluation.precision_at_x_percent(test.y, predictions,
                                                    x_percent=0.1)
    logger.debug("Precision at 10%: {} (probability cutoff {})".format(
                 round(precision10[1], 2), precision10[0]))

    evaluation.plot_precision_at_varying_percent(test.y, predictions)


def get_feature_importances(model):
    try:
        return model.feature_importances_
    except:
        pass
    try:
        return model.coef_
    except:
        pass
    return None


def pickle_config_results(pkl_file, config, test, predictions,
                          feature_importances):

    #Log experiment
    db_credentials = cfg_main['logger_uri']
    mongo_logger = Logger(db_credentials, 'models', 'cincinnati')
    #Sending model will log model name, parameters and datetime
    #Also log other important things by sending named parameters
    mongo_logger.log_model(model, features=test.feature_names,
                                  feature_importances=feature_importances,
                                  config=config,
                                  test_labels=test.y,
                                  test_predictions=predictions,
                                  test_parcels=test.parcels)

    # to_save = {"config": config,
    #            "features": test.feature_names,
    #            "feature_importances": feature_importances,
    #            "test_labels": test.y,
    #            "test_predictions": predictions,
    #            "test_parcels": test.parcels}


    # #Preppend output folder to pkl_file so results are stored there
    # path_to_pkl = os.path.join(os.environ['OUTPUT_FOLDER'], pkl_file)
    # with open(path_to_pkl, 'wb') as f:
    #     pickle.dump(to_save, f, protocol=pickle.HIGHEST_PROTOCOL)


def main():

    # config
    if len(sys.argv) <= 1:
        config_file = os.path.join(os.environ["ROOT_FOLDER"], "default.yaml")
    else:
        config_file = sys.argv[1]
    config, config_raw = configure_model(config_file)

    # datasets
    train, test, field_train, field_test = make_datasets(config)
    # instantiate models with different sets of hyperparameters
    models = grid_from_class(config["model"])

    # fit each model for all of these
    for model in models:
        #Try to run in parallel if possible
        if hasattr(model, 'n_jobs'):
            model.set_params(n_jobs=MAX_CORES)

        timestamp = datetime.datetime.now().isoformat()

        # train
        logger.info("Training {}".format(model))
        model.fit(train.x, train.y)

        # predict
        logger.info("Predicting on validation samples...")
        predicted = model.predict_proba(test.x)
        predicted = predicted[:, 1]  # probability that label is 1

        # statistics
        output_evaluation_statistics(test, predicted)
        feature_importances = get_feature_importances(model)

        # pickle
        outfile = "{prefix}{timestamp}.pkl".format(prefix=config["pkl_prefix"],
                                                   timestamp=timestamp)
        outfile = os.path.join(results_dir, outfile)
        config_raw["parameters"] = model.get_params()
        pickle_config_results(outfile, config_raw, test,
                              predicted, feature_importances)

        # generate blight probabilities for field test
        if config["prepare_field_test"]:
            logger.info("Predicting for all cincinnati parcels ")
            model.fit(field_train.x, field_train.y)

            fake_inspections_probs = model.predict_proba(field_test.x)
            # probability that label is 1
            fake_inspections_probs = fake_inspections_probs[:, 1]

            # make a csv with the predictions
            index = pd.MultiIndex.from_tuples(
                field_test.parcels, names=['parcel', 'inspection_date'])
            parcels_with_probabilities = pd.Series(
                fake_inspections_probs, index=index)
            parcels_with_probabilities.sort(ascending=False)
            outfile = os.path.join(predictions_dir,
                                   "{}.csv".format(timestamp))
            parcels_with_probabilities.to_csv(outfile)

if __name__ == '__main__':
    main()
