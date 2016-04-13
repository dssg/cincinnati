import pandas as pd
from lib_cinci import data_folder
import os
import sys

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: %s' % path_to_data_folder

input_filename = "diff_three11_2.csv"
output_filename = "diff_three11_2_clean.csv"

#Load csv file
df = pd.read_csv(input_filename, parse_dates=['REQUESTED_DATETIME'], dtype={'ZIPCODE': str})
print 'Raw file has {:,d} rows and {:,d} columns'.format(*df.shape)

if df.shape[0] == 0:
    print 'File has 0 rows, terminating...'
    sys.exit()

#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower())

#We are only using data starting from 2005
indexes = [i.year >= 2005 for i in df.requested_datetime]
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

#All values in jurisdiction_id are 'cincinnati', drop column
df.drop('jurisdiction_id', axis=1, inplace=True)
#status_notes is empty
df.drop('status_notes', axis=1, inplace=True)
#Service name has "" on each row, remove them
df.service_name = df.service_name.map(lambda s: s.replace('"', ''))
#Same with service code and description
df.service_code = df.service_code.map(lambda s: s.replace('"', ''))
df.description = df.description.map(lambda s: s.replace('"', ''))
#Service notice is just full of spaces
df.drop('service_notice', axis=1, inplace=True)
#The rest of the columns have similar problems
df.address = df.address.map(lambda s: s.replace('"', ''))
df.drop('address_id', axis=1, inplace=True)

#this is not longer needed since open data portal version does not contain
#this column
#df.drop('media_url', axis=1, inplace=True)

#Thse columns have many repeated values, not sure
#whay they are
df.drop('requested_date', axis=1, inplace=True)
df.drop('updated_date', axis=1, inplace=True)
df.drop('last_table_update', axis=1, inplace=True)
#updated_datetime is the same as requested_datetime
#no idead hat expected_datetime is
df.drop('updated_datetime', axis=1, inplace=True)
df.drop('expected_datetime', axis=1, inplace=True)

#get number and street name form address
df.address = df.address.map(lambda x: x.split(' - ')[0].replace(', CINC', ''))

#Save data frame
print 'Cleaned file has {:,d} rows and {:,d} columns. Saving on three11_clean.csv'.format(*df.shape)
df.to_csv(output_filename, index=False)