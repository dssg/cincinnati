from urllib import urlopen
import json
import subprocess
import pandas as pd
from io import StringIO
from contextlib import contextmanager

import os
import uuid
import time




def census_single_query(addr):
    """
    Query the census API with a single address.
    :param addr:
    :return:
    """
    url = "http://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={}&benchmark=9&format=json".format(addr)
    response = urlopen(url)
    data = response.readall().decode('utf-8')
    data = json.loads(data)

    if "result" not in data:
        return None
    if "addressMatches" not in data["result"]:
        return None

    matches = data["result"]["addressMatches"]
    if len(matches) == 0:
        return None
    if len(matches) > 1:
        print (addr)
        for m in matches:
            print (m["addressComponents"])
        print (matches)
        raise Exception("Too many matches")

    result = matches[0]["coordinates"]
    result = {"lat": result["y"], "lon": result["x"], "matched_address": matches[0]['matchedAddress']}
    return pd.Series(result)

@contextmanager
def make_temp_file():
    try:
        filename = '/tmp/{}.csv'.format(uuid.uuid1())
        yield filename
    finally:
        os.remove(filename)


def census_batch_query(batch_df):
    """
    Query the census API with a batch of at most 1000 addresses
    :param batch_df: Must have columns "address", "town", "state", "zip"
    :return:
    """
    with make_temp_file() as tmp:
        batch_df = batch_df[["street_address", "town", "state", "zip"]]
        batch_df.to_csv(tmp, header=False)

        # call curl
        cmd = '''curl --form addressFile=@{} --form benchmark=9 http://geocoding.geo.census.gov/geocoder/locations/addressbatch'''.format(tmp)
        args = cmd.split()
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # read results
        result =  stdout.decode('UTF-8')
        result_df = pd.read_csv(StringIO(result), header=None,
                                names=["index", "original_address", "match",
                                       "match_type", "matched_address", "coordinates", "??", "R/L"])
        result_df = result_df.set_index("index")

        # should have one line for every input line
        if len(batch_df) - len(result_df)  > 100:
            #print (stderr)
            #print (stdout)
            print (len(batch_df), len(result_df))
            raise Exception("Bad results")

        # can only use results that are a match
        result_df = result_df[result_df["match"] == "Match"]
        result_df[["lon", "lat"]] = result_df["coordinates"].apply(lambda coord: pd.Series(tuple(coord.split(","))))
        return result_df
