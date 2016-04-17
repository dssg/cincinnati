import pandas as pd
from lib_cinci import data_folder
import os

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: %s' % path_to_data_folder

#Load csv file
df = pd.read_csv("diff_sales.csv", parse_dates=['date_of_sale'],
                dtype={'house_number': int})
print 'Raw file has {:,d} rows and {:,d} columns'.format(*df.shape)

#We are only using data starting from 2012
indexes = [i.year >= 2012 for i in df.date_of_sale]
df = df[indexes]
print 'Subset from 2012 has {:,d} rows and {:,d} columns'.format(*df.shape)

#Parse address data
def format_address(x):
    number = str(x.house_number) if str(x.house_number) != 'nan' else ''
    dir_ = str(x.street_direction)  if str(x.street_direction) != 'nan' else ''
    name = str(x.street_name) if str(x.street_name) != 'nan' else ''
    non_empty = [e for e in [number, dir_, name] if e != '']
    addr = reduce(lambda x,y: x+' '+y, non_empty) if len(non_empty) else ''
    return addr

df['address'] = [format_address(x) for x in df.itertuples()]
df.drop(['street_direction', 'street_name', 'house_number'], axis=1, inplace=True)

#Add columns for geocoding
df['city'] = 'CINCINNATI'
df['state'] = 'OHIO'

#Save data frame
df.to_csv('diff_sales_clean.csv', index=False)
