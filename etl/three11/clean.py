import pandas as pd
from dstools import data_folder
import os

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(path_to_data_folder)
print 'Working in folder: %s' % path_to_data_folder

#Load csv file
df = pd.read_csv("od_cinc_311_service_reqs.csv")

#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower())

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
df.drop('media_url', axis=1, inplace=True)

#Save data frame
df.to_csv('three11_clean.csv', index=False)