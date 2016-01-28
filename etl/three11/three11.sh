#!/usr/bin/env bash
THREE11_DATA="$DATA_FOLDER/etl/three11"
TMP_FOLDER="$DATA_FOLDER/etl/three11/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

#Convert xls file
ssconvert "$THREE11_DATA/od_cinc_311_service_reqs.xls" "$TMP_FOLDER/od_cinc_311_service_reqs.csv"

#Clean dataset
python "$ROOT_FOLDER/etl/three11/clean.py"

#Generate CREATE TABLE statement
csvsql -i postgresql --tables three11 --db-schema public -d ',' "$TMP_FOLDER/three11_clean.csv" > "$TMP_FOLDER/three11.sql"
#Drop table if exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS three11;"  
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/three11.sql"  

#Upload data to the database
cat "$TMP_FOLDER/three11_clean.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.three11 FROM STDIN  WITH CSV HEADER DELIMITER ',';"

echo 'Done!'