import urllib2
from lib_cinci.db import uri
import dataset
import pandas as pd


#Step zero: read from yaml file
url = 'https://data.cincinnati-oh.gov/api/views/4cjh-bm8b/rows.csv?accessType=DOWNLOAD'
schema = 'public'
table_name = 'three11'
db_column_name = 'requested_datetime'
file_column_name = 'REQUESTED_DATETIME'

file_name = 'data.csv'

#Step one: download file from remote server
data_file = urllib2.urlopen(url)
#Dowload file replacing it if already exists
with open(file_name,'wb') as output:
    output.write(data_file.read())

#Step two: check most recent entry in the database
db = dataset.connect(uri)
table = db[table_name]
db_most_recent = table.find_one(order_by='-'+db_column_name)[db_column_name]

#Step three: subset the file to include new entries
df = pd.read_csv(file_name)
df[file_column_name] = pd.to_datetime(df[file_column_name])
is_new = df[file_column_name] > db_most_recent 
new_entries = df[is_new]

print '{:,d} new enties'.format(new_entries.shape[0])

#Step four: save new entries in a csv file
new_entries.to_csv('diff.csv', index=False)

