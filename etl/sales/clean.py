import pandas as pd
from lib_cinci import data_folder
import os

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: %s' % path_to_data_folder

#Load csv file
df = pd.read_csv("diff_sales.csv", parse_dates=['date_of_sale'],
                dtype={'st_number': int})
print 'Raw file has {:,d} rows and {:,d} columns'.format(*df.shape)

#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower())

#Parse address data
def format_address(x):
    number = str(x.st_number) if str(x.st_number) != 'nan' else ''
    dir_ = str(x.st_dir)  if str(x.st_dir) != 'nan' else ''
    name = str(x.st_name) if str(x.st_name) != 'nan' else ''
    non_empty = [e for e in [number, dir_, name] if e != '']
    addr = reduce(lambda x,y: x+' '+y, non_empty) if len(non_empty) else ''
    return addr

df['address'] = [format_address(x) for x in df.itertuples()]
df.drop(['st_dir', 'st_name', 'st_name'], axis=1, inplace=True)

#Add columns for geocoding
df['city'] = 'CINCINNATI'
df['state'] = 'OHIO'

#Save data frame
df.to_csv('diff_sales_clean.csv', index=False)
