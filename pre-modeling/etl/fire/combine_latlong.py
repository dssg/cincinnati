import pandas as pd
import os
import sys

if __name__ == '__main__':

    infile = sys.argv[1]
    outfile = sys.argv[2]

    df = pd.read_csv(infile, dtype=object)

    # if the geocoder failed, fall back on the lat/long from the API, if available
    df.loc[df.latitude.isnull()|df.longitude.isnull(), 'latitude'] = df.delivered_latitude
    df.loc[df.latitude.isnull()|df.longitude.isnull(), 'longitude'] = df.delivered_longitude

    df = df.drop(['delivered_latitude','delivered_longitude'],1)

    df.to_csv(outfile, index=False)
