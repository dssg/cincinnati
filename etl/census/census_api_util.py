from urllib2 import Request, urlopen, URLError
import pandas as pd
import numpy as np

'''
A series of utility functions for getting information out of the US census
API. Accesses the centennial census API and the American Cuummpnity Survey API. 

Includes:
lookup_cmpd_division_statistics(): for getting information about police divisions
query_census_api(): for getting information about a census block group
generate_hardcoded_data(): encodes some useful information about the two APIs
'''

def lookup_cmpd_division_statistics(connection,division,api,weight_field,fields,year,key,agg_function,verbose=False):
	'''Look up information about a police division.

	Input arguments:
	connection: a database connection object
	division: division number to look up, or '*' for all of them
	api: 'census' for centennial census, 'acs' for american community survey
	weight_field: field to use for weighting the statistics of block groups. Population ('P0010001' for census, 'B00001_001E' for ACS (I think)). Make this None if you don't want to weight stuff
	fields: list of fields to generate weighted mean statistics for
	year: year for the api
	key: api key
	agg_function: how to aggregate the fields. You would want to use np.sum for absolute population, but np.mean or np.median for something like income (assuming numpy has been imported as np)

	Note: the smallest resolution for which ACS data is available is block groups. To deal with block groups that are split across multiple police divisions, this function assumes that people are evenly distributed around a given block group. So it apportions out qualities of a block group by the fraction of the group contained in the CMPD division. '''
	
	if verbose: print '\nRetrieving CMPD division information in verbose mode'
	headnum=20
	query = '''select b.division,a.tractce10, a.namelsad10, a.blkgrpce10, st_area(st_intersection(b.geom,a.geom))/st_area(a.geom) as blkgrp_portion from mecklenburg.blockgroups_2010 as a, mecklenburg.pd_divisions as b where ST_overlaps(b.geom, a.geom) {} order by a.tractce10, a.blkgrpce10'''
	
	if (division != '*'):
		query = query.format('and b.division = \''+str(division)+'\'')
	else:
		query = query.format('')
		
	if verbose: print '\nSQL query:\n' + query
	sqlf = pd.read_sql(query, connection)
	if verbose: print '\nSQL results:\n'+str(sqlf.head(headnum))
	
	request_fields = list(fields)
	if (weight_field != None):
		request_fields.append(weight_field)
	
		
	apif = query_census_api(api,37,119,'*','*',request_fields,year,key,verbose=verbose)
	if verbose: print '\nAPI results:\n'+ str(apif.head(headnum))
	
	#For each division D, for each field F, calculate the value of F for D by taking all of the block groups {Bd} that overlap D, and multiply their value on F by the percentage of their extent that is contained in D. Then get the value for F on D by aggregating those weighted values in the manner specified in the arguments, which will typically be by summing or averaging. 
	
	apif = apif.rename(columns={'tract': 'tractce10','block group':'blkgrpce10'})
	merged = pd.merge(sqlf,apif,how='left',on=(['tractce10','blkgrpce10'])).sort(['division'])
	#get rid of any row with an na in one of its columns
	merged = merged.dropna(how='any')
	if verbose: print '\nMerged (with NaNs dropped):\n'+ str(merged.head(headnum))

	#Weight the requested columns by the occupied portion of the block group. If there is a weight field, weight that too
	if (weight_field != None):
		# merged[request_fields] =  merged[request_fields].astype('float').multiply(merged['blkgrp_portion'].astype('float'),axis='index')
		merged[weight_field] =  merged[weight_field].astype('float').multiply(merged['blkgrp_portion'].astype('float'),axis='index')
		merged[weight_field] = merged[weight_field]/merged[weight_field].mean()
		
		if verbose: print '\nWeighted:\n'+ str(merged.head(headnum))

		agg_functions = {weight_field:np.sum}
		for field in fields:
			agg_functions[field] = agg_function
	
		grouped = merged.groupby('division').agg(agg_functions)
		#grouped[fields] = grouped[fields].divide(grouped[weight_field],axis='index')
	else:		
		merged[fields] =  merged[fields].astype('float').multiply(merged['blkgrp_portion'],axis='index')
		if verbose: print '\Weighted:\n'+ str(merged.head(headnum))

		grouped = merged.groupby('division').agg(agg_function)[fields]

	

	if verbose: print '\nGrouped:\n'+ str(grouped.head(headnum))

	return grouped
	
	


def query_census_api(api,state,county,tract,blockgroup,fields,year,key,verbose=False):
	'''
	Function for querying either the centennial census API or the American
	Community Survey API. 
	Input arguments:
	api: 'census' for census, or 'acs' for American Community Survey
	state: state FIPS code. North Carolina is 37
	county: county FIPS code. Mecklenburg is 119
	tract: specify a census track or put '*' for all
	blockgroup: specify a block group or put '*' for all
	fields: a list of strings describes what fields you want to get out of the api.
		See the suggested_fields object for some useful fields
	key: a census API key
	'''
	(valid_years,base_urls,suggested_fields) = generate_hardcoded_data()

	api = str(api)
	state = str(state)
	county = str(county)
	tract = str(tract)
	blockgroup = str(blockgroup)
	#fields = ','.join((x['name'] for x in suggested_fields[api] if x['name'] != ''))
	#descs = list(x['desc'] for x in suggested_fields[api] if x['name'] != '')
	#print descs

	fieldstr = ','.join(fields)

		
	year = str(year)
	
	
	
	if (api not in valid_years):
		print 'Not a valid choice of api. Choose either \'acs\' or \'census\''
		return
	else:
		if(year not in valid_years[api]):
			print 'Not a valid year. Choose a year in: ' + str(valid_years[api])
			return
			
	base_url = base_urls[api].format(year)

	#Construct API request URL
	request_url = base_url +'?get='+fieldstr+'&for=block+group:'+blockgroup+'&in=state:'+state+'+county:'+county +'&key='+key
	
	#'+tract:'+tract+
	if verbose: print '\nAPI URL:\n'+request_url
	
	request = Request(request_url)
	try:
		response = urlopen(request)
		kittens = eval(response.read().replace("null","None"))
		headers = kittens.pop(0)
		#for i in range(0,len(descs)):
			#headers[i] = headers[i]+' - '+descs[i]
		#headers = zip(headers,descs)
		df = pd.DataFrame(kittens,columns=headers)
		df[fields]=df[fields].astype('float')
	except URLError, e:
		print 'No kittez. Got an error code:', e
		
	return df
	
'''
Defines some hardcoded data and values used by query_census_api()
'''
def generate_hardcoded_data():
	#Set some hardcoded values/background information
	valid_years = {'census':['2010', '2000', '1990'],
				   'acs':['2013', '2012', '2011','2010']}

	base_urls = {'census':'http://api.census.gov/data/{}/sf1',
				'acs':'http://api.census.gov/data/{}/acs5'}

	#some fields a user might be interested in from the two APIs. 
	suggested_fields = {
		'census':[ #More info vailable at http://www.census.gov/data/developers/data-sets/decennial-census-data.html
			{'name':'P0010001','desc':'Total population'},
			{'name':'P0030002','desc':'Total white population'}, #this seems to include hispanic people
			{'name':'P0030004','desc':'Total black population'},
			{'name':'P0030005','desc':'Total Asian population'},
			{'name':'P0030006','desc':'Total Hawaiian/pacific islander population'},
			{'name':'P0030007','desc':'Total other race population'},
			{'name':'P0030008','desc':'Total biracial population'},
			{'name':'P0040002','desc':'Total nonhispanic population'},
			{'name':'P0040003','desc':'Total hispanic population'},
			{'name':'P0100001','desc':'Total population 18 years and over'},
			{'name':'P0120002','desc':'Total male population'},
			{'name':'P0130001','desc':'Median age'},
			{'name':'P0160001','desc':'Population in households'},
			{'name':'P0170001','desc':'Average household size'},
			{'name':'P0180001','desc':'Number of households'},
			{'name':'P0180002','desc':'Number of family households'},
			{'name':'P0180003','desc':'Number of husband-wife households'},
			{'name':'H0030001','desc':'Number of housing units'},
			{'name':'H0030002','desc':'Number of occupied housing units'},
			{'name':'H0030003','desc':'Number of vacant housing units'},],
		'acs':[ #More info available at http://www.census.gov/data/developers/data-sets/acs-survey-5-year-data.html
			#Any name that ends with E, you can get the margin of error by replacing that E with an M. I won't count these separately after the first. 
			{'name':'B01003_001E','desc':'Total Population'},

			{'name':'B01001_002E','desc':'Total male population'},
			{'name':'B01001_026E','desc':'Total female population'},
			{'name':'B02001_002E','desc':'Total "white alone" population'},
			{'name':'B02001_003E','desc':'Total "black or african american alone" population'},
			{'name':'B02001_004E','desc':'Total "american indian and alaska native alone" population'},
			{'name':'B02001_005E','desc':'Total "asian alone" population'},
			{'name':'B02001_007E','desc':'Total "some other race alone" population'},
			{'name':'B01002_001E','desc':'Median age'},
			{'name':'B19001_001E','desc':'Total number of households'}, #Look near this for breakdown of households by income level
			{'name':'B19013_001E','desc':'Median household income'},
			{'name':'B03003_002E','desc':'Total "Not hispanic or latino" population'},
			{'name':'B03003_003E','desc':'Total "Hispanic or Latino" population'},
			{'name':'B19083_001E','desc':'Gini index'},
			{'name':'B19301_001E','desc':'Per capita income'},
			{'name':'B19301H_001E','desc':'Per capita income for "white alone, not hispanic or latino" population'},
			{'name':'B19301B_001E','desc':'Per capita income for "black or african american" population'},
			{'name':'B19301I_001E','desc':'Per capita income for "hispanic or lation" population'},
			{'name':'B25062_001E','desc':'Aggregate rent asked'},
			{'name':'B25061_001E','desc':'Rent asked'},
			{'name':'B25063_001E','desc':'Gross rent'},
			{'name':'B25075_001E','desc':'Value for housing units'},
			{'name':'B23025_001E','desc':'Total who answered about employment status'},
			{'name':'B23025_002E','desc':'Total in labor force'},
			{'name':'B23025_007E','desc':'Total not in labor force'},
			{'name':'','desc':''},
			{'name':'','desc':''},]}
			
	return (valid_years,base_urls,suggested_fields)
