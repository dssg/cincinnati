#!/usr/bin/env bash
#Takes csv file and uploads it to the database in the public shema

#Filename
FOLDER=$1
CSV_FILENAME=$2
TABLE_NAME=$3

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)
DB_PASSWORD=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.password)

#Drop tables if they already exist
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS $TABLE_NAME;"  

#Use csvsql to create a SQL script with the CREATE TABLE statement
echo "Uploading... csv file..."
csvsql --db "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME"  --insert  --tables $TABLE_NAME --db-schema public -d ',' "$FOLDER/$CSV_FILENAME" > "$FOLDER/$TABLE_NAME.sql"