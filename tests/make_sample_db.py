import random

import pandas as pd

import dbconfig
from sqlalchemy import create_engine
from lib_cinci.db import uri


random.seed(1024)
num_parcels = 5

engine = create_engine(engine)


def get_sample_parcels():
    parcels = """SELECT parcelid
                 FROM shape_files.parcels_cincy AS parcels
                 WHERE parcels.class IN (423, 510, 520, 530, 550, 552, 554, 555, 599) LIMIT 10;"""
    parcels = pd.read_sql(parcels, con=engine)
    parcels = random.sample(list(parcels["parcelid"].values), num_parcels)
    return parcels


def get_parcel_data(parcels):
    data = """SELECT *
              FROM shape_files.parcels_cincy AS parcels
              WHERE parcelid IN ()"""
    print (data)

