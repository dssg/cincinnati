#!/usr/bin/env bash
FOOD_SAFETY_DATA="$DATA_FOLDER/etl/food_safety"
TMP_FOLDER="$FOOD_SAFETY_DATA/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

#Convert xls file
ssconvert "$FOOD_SAFETY_DATA/od_cinc_food_safety.xls" "$TMP_FOLDER/od_cinc_food_safety.csv"

#Missing steps: clean

#Generate CREATE TABLE statement
csvsql -i postgresql --tables food_safety --db-schema public -d ',' "$TMP_FOLDER/od_cinc_food_safety.csv" > "$TMP_FOLDER/food_safety.sql"
#Drop table if exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS food_safety;"  
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/food_safety.sql"  

#Upload data to the database
cat "$TMP_FOLDER/od_cinc_food_safety.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.food_safety FROM STDIN  WITH CSV HEADER DELIMITER ',';"

echo 'Done creating food_safety table!'
