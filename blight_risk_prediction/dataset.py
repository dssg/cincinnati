#!/usr/bin/env python

import os
import pdb
import datetime
from itertools import groupby
from collections import namedtuple
import logging
import numpy as np
import pandas as pd

from blight_risk_prediction import util
from blight_risk_prediction.features.featurebot import \
    existing_feature_schemas, SchemaMissing
import config


logger = logging.getLogger(__name__)


# !!!!!!!!!!!! put all known features here !!!!!!!!!!!!!!!!!!!
feature_loaders = {"home_use": "load_home_use_features",
                   "owner_ner": "load_owner_features",
                   "crime_rate_past_year": "load_crime_features",
                   "tax_foreclosure": "load_tax_features",
                   "mean_impr_value": "load_tax_features",
                   "mean_land_value": "load_tax_features",
                   "mean_market_value": "load_tax_features",
                   "change_impr_value": "load_tax_features",
                   "change_land_value": "load_tax_features",
                   "change_market_value": "load_tax_features",
                   "crime_rate_1yr": "load_crime_new_features",
                   "crime_rate_3yr": "load_crime_new_features",
                   "crime_rate_1yr_guns": "load_crime_new_features",
                   "crime_rate_3yr_guns": "load_crime_new_features",
                   "housing_density": "load_census_features",
                   "population_density": "load_census_features",
                   "rate_1_per_household": "load_census_features",
                   "rate_2_per_household": "load_census_features",
                   "rate_3_per_household": "load_census_features",
                   "rate_4_per_household": "load_census_features",
                   "rate_5_per_household": "load_census_features",
                   "rate_6_per_household": "load_census_features",
                   "rate_7_plus_per_household": "load_census_features",
                   "rate_asian_householder": "load_census_features",
                   "rate_asian_pop": "load_census_features",
                   "rate_black_householder": "load_census_features",
                   "rate_black_pop": "load_census_features",
                   "rate_female_18_35": "load_census_features",
                   "rate_female_35_50": "load_census_features",
                   "rate_female_50_75": "load_census_features",
                   "rate_female_under_18": "load_census_features",
                   "rate_for_rent": "load_census_features",
                   "rate_households": "load_census_features",
                   "rate_male_18_35": "load_census_features",
                   "rate_male_35_50": "load_census_features",
                   "rate_male_50_75": "load_census_features",
                   "rate_male_over_75": "load_census_features",
                   "rate_male_under_18": "load_census_features",
                   "rate_mortgage_or_loan": "load_census_features",
                   "rate_native_householder": "load_census_features",
                   "rate_native_pop": "load_census_features",
                   "rate_occupied_units": "load_census_features",
                   "rate_other_race_householder": "load_census_features",
                   "rate_other_race_pop": "load_census_features",
                   "rate_owner_occupied": "load_census_features",
                   "rate_owner_occupied_asian": "load_census_features",
                   "rate_owner_occupied_black": "load_census_features",
                   "rate_owner_occupied_hispanic": "load_census_features",
                   "rate_owner_occupied_native": "load_census_features",
                   "rate_owner_occupied_no_children": "load_census_features",
                   "rate_owner_occupied_other_race": "load_census_features",
                   "rate_owner_occupied_w_children": "load_census_features",
                   "rate_owner_occupied_white": "load_census_features",
                   "rate_pop_occupied_units": "load_census_features",
                   "rate_pop_over_18": "load_census_features",
                   "rate_renter_occupied": "load_census_features",
                   "rate_renter_occupied_asian": "load_census_features",
                   "rate_renter_occupied_black": "load_census_features",
                   "rate_renter_occupied_native": "load_census_features",
                   "rate_renter_occupied_no_children": "load_census_features",
                   "rate_renter_occupied_other": "load_census_features",
                   "rate_renter_occupied_w_children": "load_census_features",
                   "rate_renter_occupied_white": "load_census_features",
                   "rate_vacant_units": "load_census_features",
                   "rate_white_householder": "load_census_features",
                   "rate_white_pop": "load_census_features",
                   "area": "load_parcel_areas",
                   "year_built": "load_year_built"}

############################################
# Functions for loading labels and features
############################################


class UnknownFeatureError(Exception):
    def __init__(self, feature):
        self.feature = feature

    def __str__(self):
        return "Unknown feature: {}".format(self.feature)


class FeatureLoader():

    """ IMPORTANT:
        Make sure that your queries do not refer to any feature_ schema.
        Instead, the correct schema will be set
        when initializing the database connection """

    def __init__(self, schema, start_date, end_date):
        if schema not in existing_feature_schemas():
            raise SchemaMissing(schema)

        # All querying is done using a raw connection.
        # In this connection set to use the relevant schema.
        # This makes sure that we grab the features from the correct schema.
        engine = util.get_engine()
        self.con = engine.raw_connection()
        self.con.cursor().execute("SET SCHEMA '{}'".format(schema))

        self.start_date = start_date
        self.end_date = end_date

    def load_labels(self, only_residential):
        logger.debug("Loading labels for [{}, {}]".format(self.start_date,
                     self.end_date))
        if only_residential:
            labels = ("SELECT inspections.* "
                      "FROM parcels_inspections AS inspections "
                      "JOIN shape_files.parcels_cincy AS parcels "
                      "ON inspections.parcel_id = parcels.parcelid "
                      "WHERE parcels.class IN (401, 402, 403, 404, "
                      "419, 423, 431, 510, 520, 530, 550, 551, 552, "
                      "554, 555, 560, 599, 996) "
                      "AND inspection_date >= %(start_date)s "
                      "AND inspection_date <= %(end_date)s")
        else:
            labels = ("SELECT * "
                      "FROM parcels_inspections AS labels "
                      "WHERE  inspection_date >= %(start_date)s "
                      "AND inspection_date <= %(end_date)s")

        labels = pd.read_sql(labels, con=self.con, params={"start_date":
                             self.start_date, "end_date": self.end_date})
        labels = labels.set_index(["parcel_id", "inspection_date"])

        logger.debug("... {} rows".format(len(labels)))
        return labels

    def load_feature_group(self, name_of_loading_method, features_to_load):
        loading_method = getattr(self, name_of_loading_method)
        return loading_method(features_to_load)

    def load_home_use_features(self, features_to_load):
        logger.debug("Loading home use features for [{}, {}]".format(
            self.start_date, self.end_date))

        # can not load all features directly, because some of them are dummy
        # variables replace these with the names of their dummy variables
        dummy_variables = {"home_use": ["single-family", "two-family",
                           "three-family", "multi-family", "mixed-use"]}
        features_to_load = self.resolve_dummy_variables(features_to_load,
                                                        dummy_variables)

        query = ("SELECT feature.*, labels.inspection_date "
                 "FROM  house_type AS feature "
                 "JOIN parcels_inspections AS labels "
                 "ON feature.parcel_id = labels.parcel_id "
                 "WHERE labels.inspection_date >= %(start_date)s "
                 "AND labels.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def load_owner_features(self, features_to_load):
        logger.debug("Loading owner features for [{}, {}]".format(
            self.start_date, self.end_date))
        query = ("SELECT feature.* "
                 "FROM named_entities AS feature "
                 "WHERE feature.inspection_date >= %(start_date)s "
                 "AND feature.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def load_parcel_areas(self, features_to_load):
        logger.debug("Loading parcel areas for [{}, {}]".format(
            self.start_date, self.end_date))
        query = ("SELECT feature.*, labels.inspection_date "
                 "FROM parc_area AS feature "
                 "JOIN parcels_inspections AS labels "
                 "ON feature.parcel_id = labels.parcel_id "
                 "WHERE labels.inspection_date >= %(start_date)s "
                 "AND labels.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def load_year_built(self, features_to_load):
        logger.debug("Loading years built for [{}, {}]".format(
            self.start_date, self.end_date))
        query = ("SELECT labels.parcel_id, feature.year_built::integer, "
                 "labels.inspection_date "
                 "FROM parc_year AS feature "
                 "JOIN parcels_inspections AS labels "
                 "ON feature.parcel_id = labels.parcel_id "
                 "WHERE labels.inspection_date >= %(start_date)s "
                 "AND labels.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def load_crime_features(self, features_to_load):
        logger.debug("Loading crime features for [{}, {}]".format(
            self.start_date, self.end_date))
        query = ("SELECT feature.* "
                 "FROM crime_old AS feature "
                 "WHERE feature.inspection_date >= %(start_date)s "
                 "AND feature.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def load_crime_new_features(self, features_to_load):
        logger.debug("Loading crime features for [{}, {}]".format(
            self.start_date, self.end_date))
        query = ("SELECT feature.* "
                 "FROM crime_new AS feature "
                 "WHERE feature.inspection_date >= %(start_date)s "
                 "AND feature.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def load_tax_features(self, features_to_load):
        logger.debug("Loading tax features for [{}, {})".format(
            self.start_date, self.end_date))
        query = ("SELECT feature.* "
                 "FROM tax  AS feature "
                 "WHERE feature.inspection_date >= %(start_date)s "
                 "AND feature.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def load_census_features(self, features_to_load):
        logger.debug("Loading census features for [{}, {})".format(
            self.start_date, self.end_date))
        query = ("SELECT feature.*, labels.inspection_date "
                 "FROM  census_2010 AS feature "
                 "JOIN parcels_inspections AS labels "
                 "ON feature.parcel_id = labels.parcel_id "
                 "WHERE labels.inspection_date >= %(start_date)s "
                 "AND labels.inspection_date <= %(end_date)s")

        features = self.__read_feature_from_db(query, features_to_load,
                                               drop_duplicates=True)
        logger.debug("... {} rows, {} features".format(len(features),
                                                       len(features.columns)))
        return features

    def __read_feature_from_db(self, query, features_to_load,
                               drop_duplicates=True):
        features = pd.read_sql(query, con=self.con,
                               params={"start_date": self.start_date,
                                       "end_date": self.end_date})

        if drop_duplicates:
            features = features.drop_duplicates(subset=["parcel_id",
                                                        "inspection_date"])

        features = features.set_index(["parcel_id", "inspection_date"])
        features = features[features_to_load]

        return features

    @staticmethod
    def resolve_dummy_variables(features_to_load, dummy_mapping):
        # replace all features that map to dummy vars by these dummy vars
        # if feature does not map to dummy vars, keep it
        # (but as a list, for consistency)
        feats = [dummy_mapping.get(feat, [feat]) for feat in features_to_load]
        # flatten list of lists
        feats = [feat for feat_list in feats for feat in feat_list]
        return feats


def group_features_by_loader(features):
    # group features by their loader function
    # - ugly because pythons groupby does not work properly, huh?
    # features = groupby(features, key=lambda feat: feature_loaders[feat])
    # y no working?
    features_grouped = []
    for loader_to_group in set(feature_loaders.values()):
        feats_this_loader = [feat for feat, loader in feature_loaders.items()
                             if feat in features and loader == loader_to_group]
        if len(feats_this_loader) > 0:
            features_grouped.append((loader_to_group, feats_this_loader))
    return features_grouped

#####################################################
# Functions for compiling training and test datasets
#####################################################

class Dataset():
    def __init__(self, parcels, x, y, feature_names):
        self.parcels = parcels
        self.x = x
        self.y = y
        self.feature_names = feature_names


def get_dataset(schema, features, start_date, end_date, only_residential):
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')
    loader = FeatureLoader(schema, start_date, end_date)

    # make sure that all features to be loaded actually exist
    for feature in features:
        if feature not in feature_loaders:
            raise UnknownFeatureError(feature)
    features = group_features_by_loader(features)

    # load inspections
    inspections = loader.load_labels(only_residential)

    # load each group of features and merge into a full dataset
    # merging makes sure we have the same index and sorting
    # for all features and inspections
    dataset = inspections
    for loading_method, feature_group in features:
        feature_df = loader.load_feature_group(loading_method, feature_group)
        dataset = dataset.join(feature_df, how='left')
        # dataset = dataset.dropna(subset=['viol_outcome'])

    # randomize the ordering
    dataset = dataset.reset_index()
    dataset = dataset.reindex(np.random.permutation(dataset.index))
    dataset = dataset.set_index(["parcel_id", "inspection_date"])


    path_to_tax = os.path.join(os.environ['OUTPUT_FOLDER'], 'tax.csv')
    dataset["mean_market_value"].to_csv(path_to_tax)

    # split up the dataset into features, labels, etc
    labels = dataset["viol_outcome"].values
    features = dataset.drop('viol_outcome', axis=1)
    parcels_inspections = dataset.index.values

    # impute missing feature values
    features = util.mean_impute_frame(features)

    logger.debug("Dataset has {} rows and {} features".format(
        len(labels), len(features.columns)))
    return Dataset(parcels_inspections, features, labels, features.columns)


def get_training_dataset(features, start_date, end_date, only_residential):
    """
    :param schema: Database schema to use
    :param features: Which features to load
    :param end_date: Inspections until this date
    :return:
    """
    logger.info("Getting features and labels for training data")

    # features are taken from the "features" schema
    schema = "features"

    return get_dataset(schema, features, start_date, end_date,
                       only_residential)


def get_testing_dataset(features, start_date, end_date, only_residential):
    """
    :param features: Which features to load
    :param start_date: Inspections from this date
    :param end_date: Inspections until this date
    :return:
    """
    logger.info("Getting features and labels for test data")

    # features are taken from the "features" schema
    schema = "features"

    return get_dataset(schema, features, start_date, end_date,
                       only_residential)

def get_field_testing_dataset(features, fake_inspection_date,
                              only_residential):
    """

    :param features: Which features to load
    :param fake_inspection_date: Date on which the inspection will take place
    :return:
    """
    logger.info("Getting features and labels for field testing training data")

    # random date very long ago (because actually the interval should
    # be open-ended on the front)
    start_date = datetime.datetime.strptime('01Jan1970', '%d%b%Y')

    # features are taken from the schema specific for this inspection date
    schema = "features_{}".format(fake_inspection_date.strftime('%d%b%Y'))

    return get_dataset(schema, features, start_date, fake_inspection_date,
                       only_residential)
