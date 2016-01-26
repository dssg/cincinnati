from __future__ import division
import grequests
from StringIO import StringIO
import pandas as pd

class BadInputError(ValueError):
    '''Raise when the input Data Frame does not contain a appropiate input'''
    def __init__(self, message, *args):
        self.message = message
        super(BadInputError, self).__init__(message, *args) 

def geocode_dataframe(df):
    '''
        Geocodes a Pandas dataframe.
        There should be an address, city, state and zip column.
        Columns can be empty (except address)
    '''
    #Check that address column does not contain null or empty strings
    bad_addresses = df.address.isnull().sum() + (df.address == '').sum()
    if bad_addresses > 0:
        e = BadInputError(message='address column cannot contain nulls or empty strings')
        raise e

    #Replace nulls with empty strings on city, state and zip
    #to 'nan' is not introduced in the census file input
    df.fillna('', inplace=True)
    #Apply function to follow input format
    #http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
    #Unique ID, Street address, City, State, ZIP
    #itertuples is faster than apply, at least in this case
    fn = lambda x: '{},{},{},{}'.format(x.address, x.city, x.state, x.zip)
    addresses = [fn(x) for x in df.itertuples()]
    #Get unique addresses and cast to a list
    #This will potentially reduce the number of unique addresses
    n_addresses = len(addresses)
    print '{} addresses received'.format(n_addresses)
    addresses = list(set(addresses))
    n_uniq_addresses = len(addresses)
    print '{} unique addresses found'.format(n_uniq_addresses)
    #Now, to each unique address, assign a unique id, this is necessary
    #to make the census API work
    id_addresses = zip(range(len(addresses)), addresses)
    fn = lambda x: '{},{}'.format(x[0], x[1])
    addresses = [fn(x) for x in id_addresses]
    #TO DO: Check that addresses do not contain commas
    #Geocode addresses using the batch census API
    census_results = geocode_list(addresses)
    #census_results is the raw output, parse it using pandas
    f = StringIO(census_results)
    #I don't see any documention about the
    #census output format, I'm guessing here
    columns = ['id', 'raw_input', 'match', 'exact', 'geocoded_address',
               'long_lat', 'col_6', 'col_7']
    res = pd.read_csv(f, names=columns)
    #Split long_lat. If long_lat is nulls, function returns an empty
    #tuple
    long_lat = res.long_lat.map(lambda s: __split_long_lat_str(s))
    res[['longitude', 'latitude']] = long_lat.apply(pd.Series)
    #Since we inly geocoded unique addresses, we may have deleted some duplicated
    #records, that makes the geocoding faster, but now for joining we need to
    #using that original address
    #IMPORTANT: this step won't work if the original address contains commas
    res['address'] = res.raw_input.map(lambda s: s.split(',')[0])
    #Keep only useful columns
    res = res[['address', 'geocoded_address', 'latitude', 'longitude']]
    #join the two dataframes
    df.set_index('address', inplace=True)
    res.set_index('address', inplace=True)
    output = df.join(res, how='left')
    #Debug: check that the set of addresses in df is equal to the set in output
    #set(df.index)==set(output.index)
    #Print some results
    n_geocoded = (output.latitude != '').sum()
    print '{} addresses geocoded'.format(n_geocoded)
    n_uniq_geocoded = (res.latitude != '').sum()
    print '{} unique addresses geocoded'.format(n_uniq_geocoded)
    print '{0:.2%} total addresses geocoded'.format(n_geocoded/n_addresses)
    return output

def geocode_list(l):
    '''
        Geocodes a list in which every element has the form
        Unique ID, Street address, City, State, ZIP
        Using http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
    '''
    #Split the list in chunks with max 1000 elements
    chunks = list(__make_chunks(l, 1000))
    #Combine each chunk so it only has one big string
    files_content = [reduce(lambda x,y: x+'\n'+y, chunk) for chunk in chunks]

    #Request parameters
    #http://stackoverflow.com/questions/25024087/mimic-curl-in-python
    url = "http://geocoding.geo.census.gov/geocoder/locations/addressbatch"
    data = {'benchmark': 'Public_AR_Census2010'}

    #Create the request objects
    rs = (grequests.post(url, data=data, files={'addressFile': a_file}) for a_file in files_content)
    #Make the calls, send 100 at a time
    responses = grequests.map(rs, size=100)
    #Get the content for each response
    contents = [r.content for r in responses]
    #Join responses
    all_responses = reduce(lambda x,y: x+'\n'+y, contents)
    return all_responses

def __split_long_lat_str(lat_long):
    if type(lat_long)==str:
        return tuple(lat_long.split(','))
    else:
        return ('','')

#Split in chunks of 1000
#http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def __make_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]