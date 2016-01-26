import pandas as pd

#from StringIO import StringIO
import numpy as np
import grequests

#Load data
df = pd.read_csv('fire.csv')

#Get unique addresses
addresses = df.address.unique()
#Check that addresses do not contain commas!

#Generate unique ids
ids = np.arange(len(addresses))
#Generate 2d array
addresses = np.column_stack((ids, addresses))

#Apply function to follow input format
#http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
#Unique ID, Street address, City, State, ZIP
fn = lambda s: '{},{},CINCINNATI,OHIO,'.format(s[0], s[1])
#Needed to convert to list because np.apply_along_axis was trimming strings :(
lines = [fn(t) for t in addresses]

#Split in chunks of 1000
#http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def make_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

chunks = list(make_chunks(lines, 1000))

#Combine all lines in each chunk
files_content = [reduce(lambda x,y: x+'\n'+y, chunk) for chunk in chunks]

#Request parameters
#http://stackoverflow.com/questions/25024087/mimic-curl-in-python
#Check with other parameters I can send...
url = "http://geocoding.geo.census.gov/geocoder/locations/addressbatch"
data = {'benchmark': 'Public_AR_Census2010'}


rs = (grequests.post(url, data=data, files={'addressFile': a_file}) for a_file in files_content)
responses = grequests.map(rs, size=100)

#Contents
contents = [r.content for r in responses]

#Join responses
all_responses = reduce(lambda x,y: x+'\n'+y, contents)

with open('responses_2015.csv', 'w') as f:
    f.write(all_responses)