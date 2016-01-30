#!/usr/bin/env bash
BULK_GEOCODER_FOLDER="$ROOT_FOLDER/bulk_geocoder"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Create address table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/address.sql"

#Join addresses in the different datasets and filter them
#to get the unique ones
python "$ROOT_FOLDER/bulk_geocoder/get_unique_addresses.py"

#Match addresses to events with a unique id

#This script creates a geometric point in each address with latitude and longitude
#with a NULL value in geom column
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/update_geoms.sql"

#Creates parcel2address table, which contains records for each parcel to its
#addresses nearby
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/parcel_to_address.sql"

#This script computes the distance for each parcel in  parcels_cincy (Note that this includes ALL
#parcels in the city)
#with each row in address. Once finished, it saves the records, so the next
#time only computes distances for the new addresses. Results are store in parcel2address
#table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/update_distances.sql"