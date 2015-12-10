#!/usr/bin/env bash
echo 'Starting python script to geocode...'

#Now perform the geocoding
python "$ROOT_FOLDER/etl/crime/geocode_crime.py"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

CRIME_DATA_FOLDER="$DATA_FOLDER/etl/crime/"
CRIME_CODE_FOLDER="$ROOT_FOLDER/etl/crime/"

#Remove merged file if exists
rm -f "$CRIME_DATA_FOLDER/geocoded/geocoding_results.csv"
#Merge all the batch results into one
cat "$CRIME_DATA_FOLDER/geocoded/"*.csv >> "$CRIME_DATA_FOLDER/geocoded/geocoding_results.csv"

#Create (temporary) geocode table in the database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CRIME_CODE_FOLDER/create_tmp_crime_lat_long.sql"

#Load data into the database
cat "$CRIME_DATA_FOLDER/geocoded/geocoding_results.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.crime__latlong FROM STDIN DELIMITER ',';"

#Remove duplicates, join geocoded data with the original crime table
#and add information on census block, tract, etc
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CRIME_CODE_FOLDER/finish_crime.sql"
