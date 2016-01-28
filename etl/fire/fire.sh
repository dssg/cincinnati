#!/usr/bin/env bash
#This script requires mdbtools to be installed
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/fire"
TMP_FOLDER="$LOCAL_DATA_FOLDER/tmp"

#MS ACCESS file
DB_FILE="$LOCAL_DATA_FOLDER/NSC.mdb"

#mkdir if tmp folder does not exists
mkdir -p $TMP_FOLDER

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#All csvfiles and postgresq tables will have this prefix
PREFIX="fire"

#Get the name of all tables
TABLES=$(mdb-tables -1 $DB_FILE)
#Set IFS variable to split over line breaks only
IFS=$'\n'
#Loop over the tables
for TABLE_NAME in $TABLES; do
    #For our csv and postgresql table, substitue any non alphanumeric character for underscores
    FILENAME=${TABLE_NAME//[^a-zA-Z0-9]/_}
    #Prefix our csv and postgres table
    FILENAME="$PREFIX"_"$FILENAME"
    #Set the path to save the csv file
    PATH_TO_CSV_FILE="$TMP_FOLDER/$FILENAME.csv"
    #Step 1: Convert table in $DB_FILE to csv files
    echo "Converting table '$TABLE_NAME' to csv... Storing file on $PATH_TO_CSV_FILE"
    mdb-export -D '%Y-%m-%d %H:%M:%S' $DB_FILE "$TABLE_NAME" > $PATH_TO_CSV_FILE
done
#Return IFS to its original value
unset IFS

#When we got the fire data, there was only one table. We are going to work
#with that file
#Step 2: clean the data, this script will also create
#a file a list of unique addresses in the dataset
echo 'Cleaning dataset, subsetting it to 2005-2014 and creating file with unique addresses'
python "$ROOT_FOLDER/etl/fire/clean.py"

#Step 3: Upload to postgres database
#generate CREATE TABLE statement
csvsql -i postgresql --tables fire --db-schema public -d ',' "$TMP_FOLDER/fire.csv" > "$TMP_FOLDER/fire.sql"
#Drop table if it already exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS fire;"
#Create table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/fire.sql"  
#Upload the csv file in the public schema
echo "Uploading fire data to the database..."
cat "$TMP_FOLDER/fire.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.fire FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo "Done creating fire table!"

#Create a unique id to identify each event
#since Incident# is not a unique identifier
echo 'Adding unique id'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "ALTER TABLE fire ADD id SERIAL;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "ALTER TABLE fire ADD PRIMARY KEY (id);"

#Step 4: Geocoding addresses
#echo 'Geocoding dataset, this may take a while...'
python "$ROOT_FOLDER/bulk_geocoder/geocode_csv.py" "$TMP_FOLDER/fire_addr.csv" "$TMP_FOLDER/fire_addr_geocoded.csv"
#Upload unique addresses to the address table
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY address(address, city, state, zip, geocoded_address, latitude, longitude) FROM '$TMP_FOLDER/fire_addr_geocoded.csv' WITH CSV HEADER DELIMITER ',';"

#Refactoring:
#Now, the responsibility of computing distances will be in a separate module
#each etl folder is only responsible for uploading their own addresses with lat,long
#using the geocode python script

#Create geom column on the database
#psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/fire/create_geom.sql"  
#Create a table to match every parcel with fire events
#limit this to a radius of certain Km
#Match parcels to calls
#echo 'Matching parcels to calls. This is going to take a while...'
#psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/fire/parcels_to_fire.sql"
#Create a view to include the matching table and the rest of the columns
#echo 'Creating view to match parcels with fire dataset columns'
#psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/fire/fire_view.sql"

echo 'Done!'
