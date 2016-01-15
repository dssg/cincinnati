#!/usr/bin/env python
import pandas as pd
import datetime
import logging
from collections import namedtuple
import sys
import psycopg2
from dstools.config import main as main_cfg
from blight_risk_prediction import util
from blight_risk_prediction.features import (ner, parcel,
                                             outcome, tax, crime, census)

logger = logging.getLogger(__name__)

# for every feature-set to generate, you need to register a function
# that can generate a dataframe containing the
# new features. you also need to set the database table in
# which to store the features
FeatureToGenerate = namedtuple("FeatureToGenerate",
                               ["table", "generator_function"])

# list all feature-sets that should be generated
features_to_generate = [FeatureToGenerate("tax", tax.make_tax_features),
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
                                           census.make_census_features)]

def existing_feature_schemas():
    engine = util.get_engine()
    schemas = "SELECT schema_name AS schema FROM information_schema.schemata"
    schemas = pd.read_sql(schemas, con=engine)["schema"]
    schemas = [s for s in schemas.values if s.startswith("features")]
    return schemas

def generate_features():
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

    # make a new table that contains one row for every parcel in Cincinnati
    # this table has three columns: parcel_id, inspection_date, viol_outcome
    # inspection_date is the one given as a parameter and
    # is the same for all parcels
    logging.info("Generating inspections table")
    inspections = outcome.generate_labels()
    inspections.to_sql("parcels_inspections", engine, chunksize=50000,
                      if_exists='fail', index=False, schema=schema)
    logging.debug("... table has {} rows".format(len(inspections)))

    # make features and store in database
    for feature in features_to_generate:
        logging.info("Generating {} features".format(feature.table))
        feature_data = feature.generator_function(con)
        feature_data = feature_data.reset_index()
        feature_data.to_sql(feature.table, engine, chunksize=50000,
                            if_exists='replace', index=False, schema=schema)
        logging.debug("... table has {} rows".format(len(feature_data)))


def generate_features_for_fake_inspection(inspection_date):
    """
    Generate fake inspections and features for some fake inspection_date

    The features and labels will be stored in schema "features_dayMonthYear"
    (according to the inspection date, e.g.
    features_01Aug2015.
    :return:
    """

    schema = "features_{}".format(inspection_date.strftime('%d%b%Y')).lower()
    if schema not in existing_feature_schemas():
        #raise SchemaMissing(schema)
        #Create schema here
        user = main_cfg['db']['user']
        password = main_cfg['db']['password']
        host  = main_cfg['db']['host']
        database  = main_cfg['db']['database']
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cur = conn.cursor()
        cur.execute("CREATE  SCHEMA %s;" % schema)
        conn.commit()
        cur.close()
        conn.close()
        print 'Creating schema %s' % schema
    else:
        print 'Using existing schema'

    # use this engine for all data storing (somehow does not work
    # with the raw connection we create below)
    engine = util.get_engine()

    # all querying is done using a raw connection. in this
    # connection set to use the relevant schema
    # this makes sure that we grab the "inspections_parcels"
    # table from the correct schema in all feature creators
    con = engine.raw_connection()
    con.cursor().execute("SET SCHEMA '{}'".format(schema))

    # make a new table that contains one row for every parcel in Cincinnati
    # this table has two columns: parcel_id, inspection_date
    # inspection_date is the one give as a parameter and is the same
    # for all parcels
    logging.info("Generating inspections table")
    inspections = outcome.make_fake_inspections_all_parcels_cincy(
       inspection_date)
    inspections.to_sql("parcels_inspections", engine, chunksize=50000,
                      if_exists='fail', index=False, schema=schema)
    logging.debug("... table has {} rows".format(len(inspections)))

    # make features and store in database
    for feature in features_to_generate:
        logging.info("Generating {} features".format(feature.table))
        feature_data = feature.generator_function(con)
        feature_data = feature_data.reset_index()
        feature_data.to_sql(feature.table, engine, chunksize=50000,
                            if_exists='replace', index=False, schema=schema)
        logging.debug("... table has {} rows".format(len(feature_data)))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        # to generate features for if an inspection happens at date d
        d = datetime.datetime.strptime(sys.argv[1], '%d%b%Y')
        print 'Generating features for %s' % d
        generate_features_for_fake_inspection(d)
    elif len(sys.argv) == 1:
        print 'Generating features for all dates...'
        # to generate features
        generate_features()
    else:
        print 'This command accepts only one parameter'