#!/usr/bin/env python
import pandas as pd
import datetime
import logging
from collections import namedtuple
import sys
import psycopg2
from dstools.config import main as main_cfg
import util
from features import (ner, parcel, outcome, tax, crime,
                                             census, three11, fire)
import argparse

logger = logging.getLogger(__name__)

# for every feature-set to generate, you need to register a function
# that can generate a dataframe containing the
# new features. you also need to set the database table in
# which to store the features
FeatureToGenerate = namedtuple("FeatureToGenerate",
                               ["table", "generator_function"])

# list all existing feature-sets
existing_features = [FeatureToGenerate("tax", tax.make_tax_features),
                         FeatureToGenerate("crime", crime.make_crime_features),
                         FeatureToGenerate("named_entities",
                                           ner.make_owner_features),
                         FeatureToGenerate("house_type",
                                           parcel.make_house_type_features),
                         FeatureToGenerate("parc_area",
                                           parcel.make_size_of_prop),
                         FeatureToGenerate("parc_year",
                                           parcel.make_year_built),
                         FeatureToGenerate("census_2010",
                                           census.make_census_features),
                         FeatureToGenerate("three11",
                                           three11.make_three11_features),
                         FeatureToGenerate("fire",
                                           fire.make_fire_features)]

tables = [t.table for t in existing_features]
tables_list = reduce(lambda x,y: x+", "+y, tables)

class SchemaMissing():
    def __init__(self, schema_name):
        self.schema_name = schema_name

    def __str__(self):
        return "Schema {} does not exist".format(self.schema_name)

def existing_feature_schemas():
    engine = util.get_engine()
    schemas = "SELECT schema_name AS schema FROM information_schema.schemata"
    schemas = pd.read_sql(schemas, con=engine)["schema"]
    schemas = [s for s in schemas.values if s.startswith("features")]
    return schemas

def generate_features(features_to_generate):
    """
    Generate labels and features for all inspections
    in the inspections database.

    The features and labels will be stored in schema
    "features". This schema must exist in the database before calling
    this function (for security reasons).
    :return:
    """
    schema = "features"

    # use this engine for all data storing (somehow does
    # not work with the raw connection we create below)
    engine = util.get_engine()

    # all querying is done using a raw connection. in this
    # connection set to use the relevant schema
    # this makes sure that we grab the "inspections_parcels"
    # table from the correct schema in all feature creators
    con = engine.raw_connection()
    con.cursor().execute("SET SCHEMA '{}'".format(schema))

    #Print the current schema by reading it from the db
    cur = con.cursor()    
    cur.execute('SELECT current_schema;')
    current_schema = cur.fetchone()[0]
    print 'Current schema is {}'.format(current_schema)
    
    # make a new table that contains one row for every parcel in Cincinnati
    # this table has three columns: parcel_id, inspection_date, viol_outcome
    # inspection_date is the one given as a parameter and
    # is the same for all parcels
    logging.info("Generating inspections table")
    try:
        inspections = outcome.generate_labels()
        inspections.to_sql("parcels_inspections", engine, chunksize=50000,
                      if_exists='fail', index=False, schema=schema)
        logging.debug("... table has {} rows".format(len(inspections)))
    except Exception, e:
        print 'Failed to create inspections table. {}'.format(e)

    # make features and store in database
    for feature in features_to_generate:
        logging.info("Generating {} features".format(feature.table))
        feature_data = feature.generator_function(con)
        #Every generator function must have a column with parcel_id, 
        #inspection_date and the correct number of rows as their
        #corresponding parcels_inspections table in the schema being used
        # TO DO: check that feature_data has the right shape and indexes
        feature_data.to_sql(feature.table, engine, chunksize=50000,
                            if_exists='replace', index=True, schema=schema)
        logging.debug("... table has {} rows".format(len(feature_data)))


def generate_features_for_fake_inspection(features_to_generate, inspection_date):
    """
    Generate fake inspections and features for some fake inspection_date

    The features and labels will be stored in schema "features_dayMonthYear"
    (according to the inspection date, e.g.
    features_01Aug2015.
    :return:
    """
    # use this engine for all data storing (somehow does not work
    # with the raw connection we create below)
    engine = util.get_engine()

    # all querying is done using a raw connection. in this
    # connection set to use the relevant schema
    # this makes sure that we grab the "inspections_parcels"
    # table from the correct schema in all feature creators
    con = engine.raw_connection()

    schema = "features_{}".format(inspection_date.strftime('%d%b%Y')).lower()
    if schema not in existing_feature_schemas():
        #Create schema here
        cur = con.cursor()
        cur.execute("CREATE  SCHEMA %s;" % schema)
        con.commit()
        cur.close()
        print 'Creating schema %s' % schema
    else:
        print 'Using existing schema'

    con.cursor().execute("SET SCHEMA '{}'".format(schema))

    # make a new table that contains one row for every parcel in Cincinnati
    # this table has two columns: parcel_id, inspection_date
    # inspection_date is the one give as a parameter and is the same
    # for all parcels
    logging.info("Generating inspections table")
    inspections = outcome.make_fake_inspections_all_parcels_cincy(inspection_date)
    inspections.to_sql("parcels_inspections", engine, chunksize=50000,
                      if_exists='replace', index=False, schema=schema)
    logging.debug("... table has {} rows".format(len(inspections)))

    # make features and store in database
    # some features depend on timestamps, e.g. crime in the last year, 
    # the temporal features take the timestamp from the parcels_inspections
    # table in the same schema and compute features based on that date
    for feature in features_to_generate:
        logging.info("Generating {} features".format(feature.table))
        feature_data = feature.generator_function(con)
        feature_data.to_sql(feature.table, engine, chunksize=50000,
                            if_exists='replace', index=True, schema=schema)
        logging.debug("... table has {} rows".format(len(feature_data)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date",
                        help=("To generate features for if an inspection happens"
                              "at certain date. e.g. 01Jul2015"), type=str)
    parser.add_argument("-f", "--features", type=str, default="all",
                            help=("Comma separated list of features to generate"
                                  "Possible values are %s. Defaults to all, which "
                                  "will generate all possible features" % tables_list))
    args = parser.parse_args()

    #Based on user selection create an array with the features to generate
    #Based on user selection, select method to use
    if args.features == 'all':
        selected_features = existing_features
    else:
        selected_tables = args.features.split(",")
        selected_features = filter(lambda x: x.table in selected_tables, existing_features)
    
    if len(selected_features)==0:
        print 'You did not select any features'
        sys.exit()
   
    selected  = [t.table for t in selected_features]
    selected = reduce(lambda x,y: x+", "+y, selected) 
    print "Selected features: %s" % selected

    if args.date:
        # to generate features for if an inspection happens at date d
        d = datetime.datetime.strptime(args.date, '%d%b%Y')
        generate_features_for_fake_inspection(selected_features, d)
    else:
        # to generate features
        generate_features(selected_features)
