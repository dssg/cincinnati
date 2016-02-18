#!/usr/bin/env bash
CRIME_CPD_FOLDER="$DATA_FOLDER/etl/crime"
TMP_FOLDER="$DATA_FOLDER/etl/crime/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

echo "Converting data from $CRIME_CPD_FOLDER"

#Step 1 - Convert raw data files to csv and store results in tmp folder
xlsx2csv -d x09 -s 1 "$CRIME_CPD_FOLDER/CRIME 2004-2006.xlsx" > "$TMP_FOLDER/crime_2004.csv"
xlsx2csv -d x09 -s 2 "$CRIME_CPD_FOLDER/CRIME 2004-2006.xlsx" > "$TMP_FOLDER/crime_2005.csv"
xlsx2csv -d x09 -s 3 "$CRIME_CPD_FOLDER/CRIME 2004-2006.xlsx" > "$TMP_FOLDER/crime_2006.csv"

xlsx2csv -d x09 -s 1 "$CRIME_CPD_FOLDER/CRIME 2007-2009.xlsx" > "$TMP_FOLDER/crime_2007.csv"
xlsx2csv -d x09 -s 2 "$CRIME_CPD_FOLDER/CRIME 2007-2009.xlsx" > "$TMP_FOLDER/crime_2008.csv"
xlsx2csv -d x09 -s 3 "$CRIME_CPD_FOLDER/CRIME 2007-2009.xlsx" > "$TMP_FOLDER/crime_2009.csv"

xlsx2csv -d x09 -s 1 "$CRIME_CPD_FOLDER/CRIME 2010-2012.xlsx" > "$TMP_FOLDER/crime_2010.csv"
xlsx2csv -d x09 -s 2 "$CRIME_CPD_FOLDER/CRIME 2010-2012.xlsx" > "$TMP_FOLDER/crime_2011.csv"
xlsx2csv -d x09 -s 3 "$CRIME_CPD_FOLDER/CRIME 2010-2012.xlsx" > "$TMP_FOLDER/crime_2012.csv"

xlsx2csv -d x09 -s 1 "$CRIME_CPD_FOLDER/CRIME 2013-2014.xlsx" > "$TMP_FOLDER/crime_2013.csv"
xlsx2csv -d x09 -s 2 "$CRIME_CPD_FOLDER/CRIME 2013-2014.xlsx" > "$TMP_FOLDER/crime_2014.csv"

#Put all files in a single CSV file
echo 'Concatenating crime_20*.csv into a single one...'
cat $TMP_FOLDER/crime_20*.csv > "$TMP_FOLDER/2004-2014.csv"

#Perform cleaning on the  CSV file
python "$ROOT_FOLDER/etl/crime/clean.py" "$TMP_FOLDER/2004-2014.csv" > "$TMP_FOLDER/2004-2014_cleaned.csv"

#Geocode
python "$ROOT_FOLDER/bulk_geocoder/geocode_csv.py" --separator ';' "$TMP_FOLDER/2004-2014_cleaned.csv" "$TMP_FOLDER/crime_geocoded.csv"

#Process geocoded file
python "$ROOT_FOLDER/bulk_geocoder/process_geocoded_csv.py" "$TMP_FOLDER/crime_geocoded.csv" "$TMP_FOLDER/crime_db.csv"

#Use csvsql to create a SQL script with the CREATE TABLE statement
csvsql -i postgresql --tables crime --db-schema public "$TMP_FOLDER/crime_db.csv" > "$TMP_FOLDER/crime.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS crime;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/crime.sql"  

#Import the data into the new create table
cat "$TMP_FOLDER/crime_db.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.crime FROM STDIN  WITH CSV HEADER DELIMITER ',';"

echo 'Done creating crime table!'

