#I THINK I CAN REMOVE THIS NOW

# coding: utf-8
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dstools.config import main as config
from dstools import data_folder
import tax_defs
import os

#Change working directory so all changes take place in the DATA_FOLDER
path_to_data_folder = data_folder.for_file(__file__)
os.chdir(path_to_data_folder)

print 'Working in folder: %s' % path_to_data_folder

username = config['db']['user']
password = config['db']['password']
host = config['db']['host']
database = config['db']['database']

engine = create_engine('postgresql://' + username + ':' + password + '@' + host + '/' + database)

fixed_names = tax_defs.field_names_2015
fixed_names.remove('LOC_ST_DIR')
#fixed_names 
df = pd.read_csv('Tax_Information2015.CSV', dtype=np.str, header=None, names=fixed_names)

#len(tax_defs.field_names_2015)
#df.shape
#for i in range(len(tax_defs.field_names_2015)):
#    print fixed_names[i], df.iloc[100][i]

df['PROPERTY_NUMBER'] = df['BOOK'] + df['PAGE'] + df['PARCEL'] + df['MLTOWN']
#df['PROPERTY_NUMBER']
df.to_sql('taxes_2015', engine, chunksize=50000)

