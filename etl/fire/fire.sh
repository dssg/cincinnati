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
    #Step 2: Upload to postgres database
    #Drop table if it already exists
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS $FILENAME;"  
    #Upload the csv file in the public schema
    echo "Uploading $PATH_TO_CSV_FILE to the database..."
    csvsql --db "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME"  --insert --tables $FILENAME --db-schema public -d ',' $PATH_TO_CSV_FILE
    echo "Done creating $FILENAME table!"
done
#Return IFS to its original value
unset IFS