#!/usr/bin/env bash
#This script requires mdbtools to be installed
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/fire"
TMP_FOLDER="$DATA_FOLDER/etl/fire/tmp"
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

#Loop over all tables in the $DB_FILE file (current file has only one table)
#Code based on https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL
mdb-tables -1 $DB_FILE | while read TABLE_NAME
do
    #Step 0: replace all non alphanumeric characters in the table name with underscores
    #http://stackoverflow.com/questions/1706431/the-easiest-way-to-replace-white-spaces-with-underscores-in-bash
    CSV_NAME=${TABLE_NAME//[^a-zA-Z0-9]/_}
    CSV_NAME="$PREFIX"_"$CSV_NAME"
    #Step 1: Convert all tables in $DB_FILE to csv files
    echo "Converting table '$TABLE_NAME' to csv... Storing file on $TMP_FOLDER/$CSV_NAME.csv"
    mdb-export -D '%Y-%m-%d %H:%M:%S' $DB_FILE "$TABLE_NAME" > "$TMP_FOLDER/$CSV_NAME.csv"
    #Step 2: Upload to postgres database
    #Drop tables if they already exist
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS $CSV_NAME;"  
    #Upload the csv file in the public schema
    echo "Uploading $CSV_NAME to the database..."
    csvsql --db "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME"  --insert --db-schema public -d ',' "$TMP_FOLDER/$CSV_NAME"
done