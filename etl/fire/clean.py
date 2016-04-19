import pandas as pd
from lib_cinci import data_folder
import os

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: {}'.format(path_to_data_folder)

#Load csv file, parse DATE column
df = pd.read_csv("fire.csv", parse_dates=['incident_date'])
print 'Raw file has {:,d} rows and {:,d} columns'.format(*df.shape)

#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower())

df.rename(columns={'street_address': 'address'}, inplace=True)

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

#Add necessary columns for the geocoding script
df['city'] = 'CINCINNATI'
df['state'] = 'OHIO'
df['zip'] = ''

#Save data frame
print 'Cleaned file has {:,d} rows and {:,d} columns. Saving on fire_clean.csv'.format(*df.shape)
df.to_csv('fire_clean.csv', index=False)
