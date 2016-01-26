#!/usr/bin/env python
#CLI interface for geocoding csv files
from geocoding_tools import geocode_dataframe
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("input", help=("Input csv file to geocode. There should be "
                                   "an address, city, state and zip column. "
                                   "Columns can be empty (except address)"),
                    type=str)
parser.add_argument("output", help="Output geocoded csv file.", type=str)
args = parser.parse_args()

#Load data
df = pd.read_csv(args.input)
res = geocode_dataframe(df)
res.to_csv(args.output)
