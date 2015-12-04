#Spatial joins for all parcels in Cincinnati with census unit of analysis

use file map_parcels_to_tracts_geocode.sql

#Import and create census features

use file census_api_util.ipynb to query the census api for 2010 census data in Cincinnati

use file census_features.ipynb to generate features from raw census data
