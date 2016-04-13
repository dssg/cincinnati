#!/usr/bin/env bash
THREE11_DATA="$DATA_FOLDER/etl/three11"
TMP_FOLDER="$DATA_FOLDER/etl/three11/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Path to update script
UPDATE_SCRIPT=$ROOT_FOLDER/lib_cinci/data_updater/update.py
#Create diff file with entries to upload to the database
$UPDATE_SCRIPT $ROOT_FOLDER/etl/three11/update.yaml

#Clean diff file
python "$ROOT_FOLDER/etl/three11/clean.py"

echo 'Generating CREATE TABLE statement...'
#Generate CREATE TABLE statement
csvsql -i postgresql --tables three11_2 --db-schema public -d ',' "$TMP_FOLDER/diff_three11_2_clean.csv" > "$TMP_FOLDER/three11_2.sql"
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/three11_2.sql"  

echo 'Uploading data...'
#Get list of columns to cpy, this is necessary since we have a PRIMARY KEY
#and we want postgres to take care of those values
COLS="$(head -n 1 $TMP_FOLDER/diff_three11_2_clean.csv)"
#Upload data to the database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.three11_2($COLS) FROM $TMP_FOLDER/diff_three11_2_clean.csv WITH CSV HEADER DELIMITER ',';"

echo 'Processing table: creating indexes, unique id and geometry column...'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/three11/process_table.sql"  

# #Match parcels to events (add indexes on parcel_id and event_id)
# echo 'Matching every parcel in cincinnati with every event in the three11 table (up to 3KM), this may take a while...'
# psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/three11/parcel2three11.sql"

echo 'Done.'
