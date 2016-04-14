import os
import pandas as pd
from sqlalchemy import create_engine
from lib_cinci.db import uri

#This script will take a csv file with addresses
#and compare them with the address table
#in the database, to determine which address are new and create
#a diff file for updating the database

#load address file
file_path = os.path.join(os.environ['DATA_FOLDER'], 'etl/unique_addresses.csv')
file = pd.read_csv(file_path)

#load address table
e = create_engine(uri)
table = pd.read_sql_table('address', e)

#find diff
#right now, the diff is a dumb string comparison.
#since we are using the same geocoder for all datasets
#we can expect the address format to be the same
diff = file[~file.address.isin(table.address)]

print '{:,d} new addresses found'.format(diff.shape[0])


output_path = os.path.join(os.environ['DATA_FOLDER'], 'etl/diff_unique_addresses.csv')
diff.to_csv(output_path, index=False)