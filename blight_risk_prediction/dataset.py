#!/usr/bin/env python
import os
import pdb
import datetime
import itertools
from collections import namedtuple
import logging
import numpy as np
import pandas as pd

from blight_risk_prediction import util
from blight_risk_prediction.features.featurebot import \
    existing_feature_schemas, SchemaMissing
from blight_risk_prediction.features.feature_parser import tables_and_columns_for_schema
import config

logger = logging.getLogger(__name__)

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

    def load_parcels_inspections(self, only_residential):
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

    def load_feature_group(self, table_name, features_to_load):
        #By convention, the method to load features from table_name
        #is load_table_name
        loading_method_name = 'load_%s' % table_name

        #If method does not exist, use generic loading method
        try:
            loading_method = getattr(self, loading_method_name)
        except Exception, e:
            logger.debug("{} does not exist. Using generic method".format(loading_method_name))
            loading_method = self.generate_loader_for_table(table_name)

        #Execute loading method and send a list of features to load
        return loading_method(features_to_load)

    def load_house_type(self, features_to_load):
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

    def load_named_entities(self, features_to_load):
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

    def load_parc_area(self, features_to_load):
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

    def load_parc_year(self, features_to_load):
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

    def load_tax(self, features_to_load):
        logger.debug("load_tax: Loading tax features for [{}, {})".format(
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

    def load_census_2010(self, features_to_load):
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

    def generate_loader_for_table(self, table):
        def load_features_from_table(features_to_load):
            table_name = table
            '''
                Generic feature loaders. Gets a list of features to load and a
                table name. Returns a pandas DataFrame with those features
            '''
            #Log table name and timestamps selected
            logger.debug("GENERIC FUNCTION: Loading {} features for [{}, {})".format(table_name,
                                             self.start_date, self.end_date))
            #SQL query to load features
	        #CONCATENATING LIKE THIS IS REALLY REALLY BAD, THIS IS JUST A TMP FIX
	        #I NEED TO REFACTOR THE WHOLE FILE
            query = ("SELECT feature.* "
                     "FROM "+table_name+"  AS feature "
                     "WHERE feature.inspection_date >= %(start_date)s "
                     "AND feature.inspection_date <= %(end_date)s")
    
            #Pass query and list of features to a function that returns the pandas
            #DataFrame
            features = self.__read_feature_from_db(query, features_to_load,
                                                   drop_duplicates=True,
                                                   table_name=table_name)
    
            #Log how many rows were loaded
            logger.debug("... {} rows, {} features".format(len(features),
                                                           len(features.columns)))
            #Return DataFrame
            return features

        return load_features_from_table
    
    def __read_feature_from_db(self, query, features_to_load,
                               drop_duplicates=True, table_name=None):
        features = pd.read_sql(query, con=self.con,
                               params={"start_date": self.start_date,
                                       "end_date": self.end_date,
                                       "table_name": table_name})
	logger.debug("Head is:\n%s\n Cols are: %s" % (features.head(3), list(features)))

        if drop_duplicates:
            features = features.drop_duplicates(subset=["parcel_id",
                                                        "inspection_date"])

        try:
            #Some features are costructed using both the parcel_id
            #and the inspection date
	    logger.debug("Setting parcel_id and inspection_date as indexes")
            features = features.set_index(["parcel_id", "inspection_date"])
        except Exception, e:
	    logger.debug("Setting parcel_id as index")
            #But some others only have parcel_id
            features = features.set_index("parcel_id")

	#Remove indexes from features to load
	if 'parcel_id' in features_to_load: features_to_load.remove('parcel_id')
	if 'inspection_date' in features_to_load: features_to_load.remove('inspection_date')
        #Since the query will load ALL COLUMNS, select only the ones listed by
        #the user
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

    #List all columns (with their respective table names) in the current schema
    tables_and_columns =  tables_and_columns_for_schema(schema)

    #the features parameters is a list of tuples of the form (table_name, column_name)
    #check that every tuple actually exists in the selected schema, if not,
    #raise and exception
    for feature in features:
        if feature not in tables_and_columns:
            raise UnknownFeatureError(feature)

    #To avoid loading each feature one by one, group them based on the table
    #they belong to
    groups = itertools.groupby(features, lambda x:x[0])
    grouped_features = []
    for key, tuples in groups:
        values = [x[1] for x in tuples]
        grouped_features.append((key, values))

    print 'Grouped features: %s' % grouped_features

    #Start loading each group and features and join them to a big dataframe,
    #but first you need to load the inspections data (parcel_id, inspection_date
    #and violation outcome).
    dataset = loader.load_parcels_inspections(only_residential)

    # load each group of features and merge into a full dataset
    # merging makes sure we have the same index and sorting
    # for all features and inspections
    for table_name, feature_group in grouped_features:
        feature_df = loader.load_feature_group(table_name, feature_group)
        dataset = dataset.join(feature_df, how='left')
        # dataset = dataset.dropna(subset=['viol_outcome'])

    # randomize the ordering
    dataset = dataset.reset_index()
    dataset = dataset.reindex(np.random.permutation(dataset.index))
    dataset = dataset.set_index(["parcel_id", "inspection_date"])

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
