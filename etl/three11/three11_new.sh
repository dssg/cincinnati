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

#Generate CREATE TABLE statement
csvsql -i postgresql --tables three11_2 --db-schema public -d ',' "$TMP_FOLDER/diff_three11_2_clean.csv" > "$TMP_FOLDER/three11_2.sql"
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/three11.sql"  
#Upload data to the database
cat "$TMP_FOLDER/three11_clean.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.three11 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
