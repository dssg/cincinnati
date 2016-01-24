import pandas as pd
from dstools import data_folder
import os

path_to_data_folder = data_folder.for_file(__file__)

os.chdir(os.path.join(path_to_data_folder, 'tmp'))
print 'Working in folder: %s' % path_to_data_folder

#Load csv file
df = pd.read_csv("od_cinc_building_permits.csv")

#Lowercase column names
df.columns = df.columns.map(lambda s: s.lower())

#Some columns have extra quotes
df.companyname = df.companyname.map(lambda s: s.replace('"', ''), na_action='ignore')
df.pin = df.pin.map(lambda s: s.replace('"', ''), na_action='ignore')
df.proposeduse = df.proposeduse.map(lambda s: s.replace('"', ''))

#Save data frame
df.to_csv('permits.csv', index=False)
