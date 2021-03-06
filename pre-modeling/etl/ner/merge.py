import os
import pandas as pd
from lib_cinci import data_folder

#Move current directory do all I/O operations take place in the corresponding
#Data folder
data_folder = data_folder.for_file(__file__)

os.chdir(data_folder)

#Create tmp file if it does not exist
if not os.path.exists('tmp'):
    print('Creating tmp folder in %s' % os.getcwd())
    os.makedirs('tmp')

#Move to tmp folder
os.chdir('tmp')

print('Changing working dir to: %s' % os.getcwd())

def read_for_year(year):
    df = pd.read_csv("owners_{}_resolved.csv".format(year))
    df["parcel_id"] = df["parcel_id"].astype(str)

    #dupes = df.groupby(level=0).filter(lambda x: len(x) > 1)
    df = df.drop_duplicates(subset='parcel_id')

    df = df.set_index("parcel_id")
    entities = df["entity"]
    entities.name = "owner_"+str(year)
    
    return entities


owners = [read_for_year(y) for y in range(2007, 2016)]
merged = pd.concat(owners, axis=1)
merged = merged.reset_index()
merged = merged.rename(columns={"index": "parcel_id"})

output='owners_2007-2015.csv'
merged.to_csv(output, index=False)

print('Done! File saved to: %s/%s' % (os.getcwd(), output))
