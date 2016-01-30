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
parser.add_argument("-sep", "--separator", help="separator in the file, defaults to ','",
                    type=str, default=',')
args = parser.parse_args()

#Load data
df = pd.read_csv(args.input, sep=args.separator)
res = geocode_dataframe(df)
res.to_csv(args.output, index=False)
