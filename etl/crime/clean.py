import pandas as pd
from lib_cinci import data_folder
import os
import sys

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: %s' % path_to_data_folder

input_filename = "diff_crime.csv"
output_filename = "diff_crime_clean.csv"

#Load csv file
df = pd.read_csv(input_filename, index_col='OccurredOn', parse_dates=['OccurredOn'])
print 'Raw file has {:,d} rows and {:,d} columns'.format(*df.shape)

#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower())

#Rename some columns
mapping = {'location': 'address',
           'addressstate': 'state'}
df.index.rename('occurred_on', inplace=True)
df.rename(columns=mapping, inplace=True)

#We are only using data starting from 2012
df = df[df.index.year >= 2012]
print 'Subset from 2012 has {:,d} rows and {:,d} columns'.format(*df.shape)

#Add zip column (this is needed for geocoding.py script to work)
df['zip'] = ''

#Check how many rows have empty addresses
print '{:,d} rows with empty address, removing those'.format(df.address.isnull().sum())
#Remove rows without address
df = df[df.address.notnull()]

#Check for duplicates
duplicates = df.duplicated()
n_duplicates = duplicates.sum()
print 'Found {:,d} duplicates, dropping them'.format(n_duplicates)
df = df[~duplicates]


#Save data frame
print 'Cleaned file has {:,d} rows and {:,d} columns. Saving on diff_crime_clean.csv'.format(*df.shape)
df.to_csv(output_filename)