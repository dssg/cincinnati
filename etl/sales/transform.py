"""
Take tab-delimited csv data (as produced during extract step and do data transformation.
"""


import pandas as pd
from attributes import plain_text_names

input_csv = "/tmp/salesinfo.csv"
output_csv = "/tmp/salesinfo_converted.csv"

df = pd.read_csv(input_csv, sep="\t")

# many columns have no values at all, they need to go
df = df.dropna(axis=1, how='all')

# also the names are bad
#df = df.rename(columns=plain_text_names)

# and some columns should have different types
df['DATESALE'] = pd.to_datetime(df['DATESALE'].astype(str), format='%Y%m%d')

binary = ["FINCUR_USE", "DELETED"]
for col in binary:
    assert(len(df[col].isin(['T', 'F']) == len(df)))
    df[col] = df[col].apply(lambda v: 1 if v == "T" else 0)

df.to_csv(output_csv)
