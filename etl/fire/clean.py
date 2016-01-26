import pandas as pd
from dstools import data_folder
import os

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: %s' % path_to_data_folder

#Load csv file and parse DATE column
df = pd.read_csv("fire_1997_2014_CFS.csv", parse_dates=['DATE'])
#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower().replace('#', ''))
#We are only using data starting from 2005
indexes = [i.year >= 2005 for i in df.date]
df = df[indexes]

#Strip some columns
#csvsql has a bug that is not producing the
#correct length in the CREATE TABLE script
#if strings have leading/trailing spaces
df.incident = df.incident.map(lambda s: s.strip())
df.pc = df.pc.map(lambda s: s.strip())
df.signal = df.signal.map(lambda s: s.strip())

#Check how many rows have empty addresses
print '{} rows with empty address, removing those.'.format(df.address.isnull().sum())
#Remove rows without address
df = df[df.address.notnull()]
#Add necessary columns for the geocoding script
df['city'] = 'CINCINNATI'
df['state'] = 'OHIO'
df['zip'] = ''

#Save data frame
df.to_csv('fire.csv', index=False)
