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

#Missing steps: clean data

#Generate CREATE TABLE statement
csvsql -i postgresql --tables permits --db-schema public -d ',' "$TMP_FOLDER/od_cinc_building_permits.csv" > "$TMP_FOLDER/permits.sql"
#Drop table if exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS permits;"  
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/permits.sql"  

#Upload data to the database
cat "$TMP_FOLDER/od_cinc_building_permits.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.permits FROM STDIN  WITH CSV HEADER DELIMITER ',';"

echo 'Done creating permits table!'