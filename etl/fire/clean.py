import pandas as pd
from lib_cinci import data_folder
import os
import re

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(path_to_data_folder)
tmpdir = os.path.join(path_to_data_folder, 'tmp')
print 'Working in folder: {}'.format(path_to_data_folder)

# load the downloaded files
yearlyFiles = []
for thisFile in os.listdir('.'):
    if thisFile.startswith("fire_201"):
        df = pd.read_csv(thisFile, dtype=object)
        df['incident_date'] = pd.to_datetime(df.incident_date)
        df['alarm_date_time'] = pd.to_datetime(df.alarm_date_time)
        df['unit_clear_date_time'] = pd.to_datetime(df.unit_clear_date_time)
        yearlyFiles.append(df)

for df in yearlyFiles:

    # lowercase columns names
    df.columns = df.columns.map(lambda s: s.lower())
    
    # rename address
    df.rename(columns={'street_address': 'address'}, inplace=True)

    # one file has a incident_guid column, discard
    if 'incident_guid' in df.columns:
        df.drop('incident_guid',1, inplace=True)

    # some files have location columns that are like 
    # 'CINC 45211\n(39.152816063000046, -84.60056918599997)'
    if 'location' in df.columns:

        if 'zip' not in df.columns:
            df['zip'] = df.location.str.extract('\s(\d{5})')

        if 'city' not in df.columns:
            df['city'] = df.location.str.extract('^(.*)\s\d{5}').str.upper()
            df.loc[df.city=='CINC','city'] = 'CINCINNATI'

        df.drop('location',1, inplace=True)

    else:
        if 'city' not in df.columns:
            df['city'] = 'CINCINNATI'
        if 'zip' not in df.columns:
            df['zip']  = ''

    # probably save to fill gaps with 'Cincinnati'
    df.loc[df.city=='', 'city'] = 'CINCINNATI'
    df.loc[:, 'city'] = df.city.fillna('CINCINNATI')
    df['state'] = 'OHIO'

# concatenate files
df = pd.concat(yearlyFiles, axis=0, ignore_index=True)

print 'Raw file has {:,d} rows and {:,d} columns'.format(*df.shape)

#Check how many rows have empty addresses
print '{:,d} rows with empty address, removing those'.format(df.address.isnull().sum())
#Remove rows without address
df = df[df.address.notnull()]

#Check for duplicates
duplicates = df.duplicated()
n_duplicates = duplicates.sum()
print 'Found {:,d} duplicates, dropping them'.format(n_duplicates)
df = df[~duplicates]

#Strip some columns
#csvsql has a bug that is not producing the
#correct length in the CREATE TABLE script
#if strings have leading/trailing spaces
print 'Removing leading and trailing spaces from some columns'
df.address = df.address.map(lambda s: s.strip())

#Save data frame in TMP folder
print 'Cleaned file has {:,d} rows and {:,d} columns. Saving on fire_clean.csv'.format(*df.shape)
df.to_csv(os.path.join(tmpdir, 'fire_clean.csv'), index=False)
