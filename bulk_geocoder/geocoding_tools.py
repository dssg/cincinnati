from __future__ import division
import grequests
import pandas as pd
import re

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
    #bad_addresses = df.address.isnull().sum() + (df.address == '').sum()
    #if bad_addresses > 0:
    #    e = BadInputError(message='address column cannot contain nulls or empty strings')
    #    raise e

    #Replace nulls with empty strings on city, state and zip
    #to 'nan' is not introduced in the census file input
    df.fillna('', inplace=True)
    #Apply function to follow input format
    #http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
    #Unique ID, Street address, City, State, ZIP
    #itertuples is faster than apply, at least in this case
    fn = lambda x: '{},{},{},{}'.format(x.address, x.city, x.state, x.zip)
    addresses = [fn(x) for x in df.itertuples()]
    df['raw_input'] = addresses
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
    #I don't see any documention about the
    #census output format, I'm guessing here
    res = pd.DataFrame(census_results)
    res.columns = ['id', 'raw_input', 'match', 'exact', 'geocoded_address',
               'long_lat', 'col_6', 'col_7']
    #Split long_lat. If long_lat is nulls, function returns an empty
    #tuple
    long_lat = res.long_lat.map(lambda s: __split_long_lat_str(s))
    res[['longitude', 'latitude']] = long_lat.apply(pd.Series)
    #Since we inly geocoded unique addresses, we may have deleted some duplicated
    #records, that makes the geocoding faster, but now for joining we need to
    #using that original address
    #IMPORTANT: this step won't work if the original address contains commas
    res['address'] = res.raw_input.map(lambda s: s.split(',')[0])
    #join the two dataframes
    #Now drop rows that could no be geocoded
    res = res.loc[res.geocoded_address.notnull()]
    n_geocoded = len(res.index)
    print '{} addresses geocoded'.format(n_geocoded)
    #Keep only useful columns
    res = res[['raw_input', 'geocoded_address', 'latitude', 'longitude']]
    #Split geocoded_address in their different elements
    address_elements = res.geocoded_address.map(lambda s: s.split(','))
    res[['address', 'city', 'state', 'zip']] = address_elements.apply(pd.Series)
    #Census api adds some spaces, delete them to match
    res.raw_input = res.raw_input.map(lambda x: x.replace(', ', ','))
    #Do a left join
    output = df.merge(res, on='raw_input', how='left', suffixes=('', '_census'))
    #Remove raw_input
    output.drop('raw_input', axis=1, inplace=True)
    #Debug: check that the set of addresses in df is equal to the set in output
    #set(df.index)==set(output.index)
    #Print some results
    n_total_geocoded = output.address_census.notnull().sum()
    print '{0:.2%} total addresses geocoded'.format(n_total_geocoded/n_addresses)
    return output

def geocode_list(l):
    '''
        Geocodes a list in which every element has the form
        Unique ID, Street address, City, State, ZIP
        Using http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
    '''
    #Get ids in the list
    to_geocode = len(l)
    remaining_ids = set([element.split(',')[0] for element in l])
    geocoded = []
    try_again = True

    while try_again:
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
        #Make the calls, send in batches
        responses = grequests.map(rs, size=50)
        #Get the content for each response
        contents = [r.content for r in responses]
        #Parse each content received and return
        #parse elements
        valid = __parse_contents(contents)
        print 'Geocoded {} out of {}. {} on this attempt.'.format(len(geocoded),
                                                            to_geocode,
                                                            len(valid))
        #Add elements to the geocoded list
        geocoded.extend(valid)
        remaining_ids = remaining_ids - set([e[0] for e in valid])
        l = [e for e in l if e.split(',')[0] in remaining_ids]   
        #Try gain only if in this attempt, the api geocoded_address
        #at least one
        try_again = len(valid)>0
        if not try_again:
            print 'Couldnt geocode any on this attempt. Finishing...'
    return geocoded

def __parse_contents(contents):
    '''
        Check the responses returned, return a list with
        the ones that you got right and another one with those
        that had errors
    '''
    #Split ever line in every content
    lists_of_lines = [c.split('\n') for c in contents]
    #Flatten list
    lines = [item for sublist in lists_of_lines for item in sublist] 
    #Remove empty lines
    non_empty_lines = [line for line in lines if len(line)>0]
    #Get lines that have Match
    valid = [__parse_line(line) for line in non_empty_lines if 'Match' in line]
    return valid


def __parse_line(line):
    quoted = re.compile('"[^"]*"')
    elements = quoted.findall(line)
    elements = [e.replace('"', '').strip() for e in elements]
    return elements

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
