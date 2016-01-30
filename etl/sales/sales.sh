#!/usr/bin/env bash
SALES_FOLDER="$DATA_FOLDER/etl/sales"
TMP_FOLDER="$DATA_FOLDER/etl/sales/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

echo "Converting data from $SALES_FOLDER"

#Convert raw data to tsv
python "$ROOT_FOLDER/etl/sales/extract.py" "$SALES_FOLDER/salesinfo.txt" > "$TMP_FOLDER/salesinfo.tsv"
#transform data and export to csv
python "$ROOT_FOLDER/etl/sales/transform.py" "$TMP_FOLDER/salesinfo.tsv" "$TMP_FOLDER/salesinfo.csv"

#Clean dataset
python "$ROOT_FOLDER/etl/sales/clean.py"
echo 'Geocoding dataset, this may take a while...'
python "$ROOT_FOLDER/bulk_geocoder/geocode_csv.py" "$TMP_FOLDER/sales_clean.csv" "$TMP_FOLDER/sales_geocoded.csv"

#Process geocoded file
python "$ROOT_FOLDER/bulk_geocoder/process_geocoded_csv.py" "$TMP_FOLDER/sales_geocoded.csv" "$TMP_FOLDER/sales_db.csv"

#Generate CREATE TABLE statement
csvsql -i postgresql --tables sales --db-schema public -d ',' "$TMP_FOLDER/sales_db.csv" > "$TMP_FOLDER/sales.sql"
#Drop table if exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS sales;"  
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/sales.sql"  

#Upload data to the database
cat "$TMP_FOLDER/sales_db.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.sales FROM STDIN  WITH CSV HEADER DELIMITER ',';"

#Create index, this is going to speed up joins for feature generation
#when looking for events that happened shortly before an inspection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE INDEX ON sales (datesale);"

echo 'Done creating sales table!'
