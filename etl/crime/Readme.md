### Import the CPD crime data into postgres

Use xlsx2csv to convert file by file and sheet by sheet into csv

    xlsx2csv -d x09 -s 1 CRIME\ 2004-2006.xlsx > 2004.csv
    xlsx2csv -d x09 -s 2 CRIME\ 2004-2006.xlsx > 2005.csv


Put them all into a single file
    
    cat *.csv >> 2004-2014.csv

Do some data cleaning using python

    python crime.py 2004-2014.csv > 2004-2014_cleaned.csv

Use csvsql to create a CREATE TABLE from the csv and create the table using psql
   
    csvsql -i postgresql --tables crime --db-schema public -d ';' 2004-2014_cleaned.csv > crime.sql    
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME < crime.sql	

Import the actual data into the new table

    cat 2004-2014_cleaned.csv | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.crime FROM STDIN  WITH CSV HEADER DELIMITER ';';"

### Geocode all the addresses

Geocode using the census api. Sending batches of 1000 addresses at a time to the census api. This process takes a lot of
time, so geocoding results for each batch are store in directory geocoded

    mkdir geocoded
    python geocode_crime.py
    
Merge all the batch results into one

    cat geocoded/*.csv >> geocoding_results.csv

Create (temporary) geocode table in the database 

    CREATE TABLE public.crime__latlong (
	 incident_number VARCHAR(12), 
	 latitude FLOAT,
	 longitude FLOAT);
	
Load data into the database

    cat geocoding_results.csv| psql -h $DB_HOST -U $DB_USER \
    -d $DB_NAME -c "\COPY public.crime__latlong FROM STDIN DELIMITER ',';"
    
There are some 50 duplicate incident numbers, delete those

    CREATE TEMPORARY TABLE duplicate_incidents 
    AS (SELECT incident_number
        FROM public.crime__latlong
        GROUP BY incident_number
       HAVING COUNT(*) > 1)
       
    DELETE FROM public.crime__latlong
    WHERE incident_number IN (SELECT incident_number FROM duplicate_incidents)


Join existing crime table with gecoded latitude/longitude, add also geometry column for better postgis experience

    CREATE TEMPORARY TABLE crime_geocoded__temp AS 
    (SELECT crime.*, 
        geo.latitude, 
        geo.longitude, 
        ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude),4269), 3735) AS geom   --4269 is census latitude / longitude, 3735 is cincinnati
    FROM public.crime AS crime
    LEFT OUTER JOIN public.crime__latlong AS geo
    ON crime.incident_number = geo.incident_number);
    
Finally, add also information on census block, tract, etc

    CREATE TABLE public.crime_geocoded AS (
    SELECT crime.*, census.block, census.tract, census.blkgrp
    FROM crime_geocoded__temp AS crime
    LEFT OUTER JOIN shape_files.census_blocks AS census
    ON ST_WITHIN(crime.geom, census.geom));

Don't need the latlong table anymore. The temporary tables are deleted automatically at the end of the session

    DROP TABLE public.crime__latlong
    
    
