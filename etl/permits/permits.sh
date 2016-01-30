#!/usr/bin/env bash
PERMITS_DATA="$DATA_FOLDER/etl/permits"
TMP_FOLDER="$DATA_FOLDER/etl/permits/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

#Convert xls file
ssconvert "$PERMITS_DATA/od_cinc_building_permits.xls" "$TMP_FOLDER/od_cinc_building_permits.csv"

#Clean data
python "$ROOT_FOLDER/etl/permits/clean.py"

#Generate CREATE TABLE statement
csvsql -i postgresql --tables permits --db-schema public -d ',' "$TMP_FOLDER/permits_clean.csv" > "$TMP_FOLDER/permits.sql"
#Drop table if exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS permits;"  
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/permits.sql"  

#Upload data to the database
cat "$TMP_FOLDER/permits_clean.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.permits FROM STDIN  WITH CSV HEADER DELIMITER ',';"

echo 'Almost done, creating indexes, unique id and geometry column...'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/permits/process_table.sql"  

echo 'Done creating permits table!'

#Match parcels to events (add indexes on parcel_id and event_id)
echo 'Matching every parcel in cincinnati with every event in the permits table (up to 3KM), this may take a while...'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/permits/parcel2permits.sql"  

