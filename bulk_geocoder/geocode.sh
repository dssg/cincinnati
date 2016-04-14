#!/usr/bin/env bash
BULK_GEOCODER_FOLDER="$ROOT_FOLDER/bulk_geocoder"
ETL_FOLDER="$DATA_FOLDER/etl/"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Create address table if it doesn't exist, also create indexes
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/address.sql"

#Join addresses in the different datasets and filter them
#to get the unique ones. If you incorporate a new dataset
#with addresses, you must add it manually to get_unique_addresses.py
python "$ROOT_FOLDER/bulk_geocoder/get_unique_addresses.py"

#Find the difference between the unique addresses file and the addresses
#in the database
python "$ROOT_FOLDER/bulk_geocoder/update.py"

#Upload data to the database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY address(address, zip, latitude, longitude) FROM '$ETL_FOLDER/diff_unique_addresses.csv' WITH CSV HEADER DELIMITER ',';"

#This script creates a geometric point in each address with latitude and longitude
#with a NULL value in geom column
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/update_geoms.sql"

#Using the address table (which contains unique addresses),
#add a new column in fire, crime and sales with the corresponding address_id
echo 'Mapping addresses in addreess table with events in fire, crime and sales'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/match_events_with_address.sql"

#Creates parcel2address table, which will store records for each parcel to its
#addresses nearby. This script only creates the table and does not perform any
#computation
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/parcel_to_address.sql"

#Creates already_computed_addresses table which keeps track of addresses
#that were already used for calculating distances to parcels
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/already_computed_addresses.sql"

#This script computes the distance for each parcel in  parcels_cincy (Note that this includes ALL
#parcels in the city)
#with each row in address. Once finished, it saves the records, so the next
#time only computes distances for the new addresses. Results are store in parcel2address
#table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/update_distances.sql"