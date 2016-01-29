import pandas as pd
from dstools import data_folder
import os

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: {}'.format(path_to_data_folder)

#Load csv file, parse DATE column
df = pd.read_csv("fire_1997_2014_CFS.csv", parse_dates=['DATE'])
print 'Raw file has {:,d} rows and {:,d} columns'.format(*df.shape)

#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower().replace('#', ''))

#We are only using data starting from 2005
indexes = [i.year >= 2005 for i in df.date]
df = df[indexes]
print 'Subset from 2005 has {:,d} rows and {:,d} columns'.format(*df.shape)

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
df.incident = df.incident.map(lambda s: s.strip())
df.pc = df.pc.map(lambda s: str(s).strip())
df.signal = df.signal.map(lambda s: s.strip())
df.address = df.address.map(lambda s: s.strip())

#Get unique addresses
unique_addresses = df.address.unique()
print 'Found {:,d} unique addresses. Saving on fire_addr.csv'.format(len(unique_addresses))

#Build address dataframe
addr = pd.DataFrame({'address': unique_addresses})
#Add necessary columns for the geocoding script
addr['city'] = 'CINCINNATI'
addr['state'] = 'OHIO'
addr['zip'] = ''
addr.to_csv('fire_addr.csv', index=False)

#Save data frame
print 'Cleaned file has {:,d} rows and {:,d} columns. Saving on fire.csv'.format(*df.shape)
df.to_csv('fire.csv', index=False)
