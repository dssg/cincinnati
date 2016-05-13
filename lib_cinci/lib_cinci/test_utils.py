from datetime import datetime

import pandas as pd
from pandas.util import testing
import sqlite3


def iso_date(date_str):
    date_str = datetime.strptime(date_str, '%d%b%Y')
    return date_str.isoformat()


def date(date_str):
    return datetime.strptime(date_str, '%d%b%Y')


def timestamp(date_str):
    d = datetime.strptime(date_str, '%d%b%Y')
    return pd.to_datetime(d)


class Database():
    def __init__(self):
        self.con = sqlite3.connect(':memory:')

        # sqlite3 and postgres have slightly different ways of querying and handling parameters
        # -> need to rewrite the query -> need to re-point pandas read_sql (evil!)
        self.pandas_read_sql = pd.read_sql   # copy of pointer to pandas read_sql
        pd.read_sql = self.my_read_sql       # own read_sql that first rewrites query and then calls pandas read_sql

    def my_read_sql(self, query, con, params={}):
        query = self.rewrite_query(query, params)
        return self.pandas_read_sql(query, self.con, params=params)

    def rewrite_query(self, query, params):
        # postgres uses (param)s format, sqlite3 uses :param format
        for param in params:
            query = query.replace("%({})s".format(param), ":{}".format(param))

        # also sqlite3 can not deal with the whole schema business
        query = query.replace(" public.", " ")
        query = query.replace(" features.", " ")
        return query

    def close(self):
        self.con.close()
        pd.read_sql = self.pandas_read_sql  # reset evil stuff so that next test can run


class FeatureDatabase(Database):

    def add_labels(self, label_data):
        df = pd.DataFrame(label_data)
        df.to_sql(name="features_labelled_data_time", con=self.con, index=False)

    def add_crime(self, crime_data):
        df = pd.DataFrame(crime_data)
        df.to_sql(name="crime", con=self.con, index=False)


class RawDatabase(Database):

    def add_crime(self, incident_number, date_reported, offense_title="", weapon="", tract="", block="", blkgrp=""):
        df = pd.Series({"incident_number": incident_number, "date_reported": date(date_reported),
                        "offense_title": offense_title, "weapon": weapon,
                        "tract": tract, "block": block, "blkgrp": blkgrp})
        df.to_sql(name="crime", con=self.con, if_exists="append")


def assert_frame_equal(expected_df, actual_df):
    expected_df = expected_df.copy().sort(axis=1).sort(axis=0)
    actual_df = actual_df.copy().sort(axis=1).sort(axis=0)
    testing.assert_frame_equal(expected_df, actual_df, check_names=True)
