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
#signal column has some extra spaces
df.signal = df.signal.map(lambda s: s.replace(' ', ''))
#We are only using data starting from 2005
indexes = [i.year >= 2005 for i in df.date]
df = df[indexes]

#Save data frame
df.to_csv('fire.csv', index=False)
