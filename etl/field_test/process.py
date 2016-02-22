import pandas as pd
import os
import re
from dstools.db import uri
from sqlalchemy import create_engine

e = create_engine(uri)

def clean_column_name(s):
    s = s.strip()
    s = re.sub('[^0-9a-zA-Z]+', '_', s)
    s = s.lower()
    return s

path_to_tmp = os.path.join(os.environ['DATA_FOLDER'], 'etl/field_test/tmp')

#Load files with summer results
a = pd.read_csv(os.path.join(path_to_tmp, '8-21-2015.csv'), parse_dates=['INSP DATE'])
b = pd.read_csv(os.path.join(path_to_tmp, '8-24-2015.csv'), parse_dates=['INSP DATE'])
#Merge them into a single dataframe
df = a.append(b)

#Cleaning
df.dropna(axis=1, how='all', inplace=True)
df.columns = df.columns.map(clean_column_name)
df.rename(columns={'parcel_no':'parcel_id', 'violations_':'viol_outcome'}, inplace=True)
df.viol_outcome = df.viol_outcome.map({'YES': 1, 'NONE': 0})

#Save to the field_tests table, id table exists append results
df.to_sql('field_tests', e, if_exists='replace', index=False)