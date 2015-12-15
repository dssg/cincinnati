#!/usr/bin/env bash
#This script requires mdbtools to be installed
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/fire"
TMP_FOLDER="$DATA_FOLDER/etl/fire/tmp"

#mkdir if tmp folder does not exists
mkdir -p $TMP_FOLDER

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)


#Loop over all tables in the NSC.mdb file (current file has only one table)
#Code based on https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL
mdb-tables -1 NSC.mdb | while read table_name
do
    #Step 1: Convert all tables in NSC.mdb to csv files
    echo "Converting table $table_name to csv... Storing file on $TMP_FOLDER"
    mdb-export -D '%Y-%m-%d %H:%M:%S' NSC.mdb "$table_name" > "$TMP_FOLDER/$table_name.csv"
    #"$TMP_FOLDER/${table_name}.csv"

    #Step 2: Upload to postgres database
    #Drop tables if they already exist
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS fire;"  
    #Use csvsql to create a SQL script with the CREATE TABLE statement
    echo "Uploading csv file..."
    #TO DO: change hardcoded table name
    csvsql --db "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME"  --insert --tables fire --db-schema public -d ',' "$TMP_FOLDER/1997-2014 CFS.csv"
    # > "$FOLDER/$TABLE_NAME.sql"
done

