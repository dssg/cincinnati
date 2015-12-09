#!/usr/bin/env python

import sys
from sqlalchemy import create_engine
import pandas as pd
import time
import glob

import dbconfig
from geocode import census_batch_query

def format_address_url(address):
    """
    Format an address from the crime database such that it works with a call to the Census single-address geocode
    web api.
    :param address:
    :return:
    """
    addr_split = address.split(" ")
    addr_split = [a.capitalize() for a in addr_split]
    address = "+".join(addr_split)
    address += "%2CCincinnati"
    return address

def format_address_batch(address):
    """
    Format an address such that it works with a call to the Census batch-address geocode api
    :param address:
    :return:
    """
    addr_split = address.split(" ")
    addr_split = [a.capitalize() for a in addr_split]
    address = " ".join(addr_split)
    address = {"street_address": address, "town": "Cincinnati", "state": "OH", "zip": ""}
    return pd.Series(address)


def crime_data_in_chunks():
    """
    Census only allows chunks of 1000 addresses
    :return:
    """
    engine = create_engine('postgresql://{conf.user}:{conf.password}@{conf.host}:5432/{conf.database}'.format(conf=dbconfig))
    addresses = ("SELECT * FROM public.crime where address IS NOT NULL AND LENGTH(address) > 0")
    for i, ch in enumerate(pd.read_sql(addresses, con=engine, chunksize=1000)):
        ch = ch.set_index("incident_number")
        yield i, ch

def geocode_chunk(crime_df):
    address_df =  crime_df["address"].apply(format_address_batch)
    geocoded_df = census_batch_query(address_df)
    geocoded_df = geocoded_df[["lat", "lon"]]
    geocoded_df = geocoded_df.rename(columns={"index": "incident_number"})
    print ("...geocoded")
    return geocoded_df


def download_dataset():
    for i, chunk in crime_data_in_chunks():
        chunk.to_csv("addresses/{}.csv".format(i), header=True)


def geocode_dataset():
    chunks = sorted(glob.glob("addresses/*.csv"))
    already_geocoded = sorted(glob.glob("geocoded/*.csv"))
    already_geocoded = [int(g.replace("geocoded/", "").replace(".csv", "")) for g in already_geocoded]
    failed = []

    for chunk_file in chunks:
        try:
            chunk_index = int(chunk_file.replace("addresses/", "").replace(".csv", ""))
            if chunk_index in already_geocoded:
                continue
            print ("Chunk {}".format(chunk_file))
            chunk = pd.read_csv(chunk_file, index_col=0)
            chunk = geocode_chunk(chunk)
            chunk.to_csv("geocoded/{}.csv".format(chunk_index), header=False)
        except:
            print("...failed: "+str(sys.exc_info()[0]))
            failed.append(chunk_file)
    return failed

# Step one: download the whole dataset in chunks of 1000 addresses and store as csv
download_dataset()

# Step two: geocode the chunks
failed = geocode_dataset()
print(", ".join(failed)) # will have to run these again
