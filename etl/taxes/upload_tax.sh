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

#Use csvsql to create a SQL script with the CREATE TABLE statement
echo "Generating CREATE TABLE statement from csv file..."
#For now, add the no inference parameter to avoid trouble with certain numeric columns that have commas
csvsql --no-inference -i postgresql --tables $TABLE_NAME --db-schema public -d ',' "$FOLDER/$CSV_FILENAME" > "$FOLDER/$TABLE_NAME.sql"
#Drop tables if they already exist
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS $TABLE_NAME;"  
#Run the CREATE TABLE statements on the database
echo "Running CREATE TABLE statement..."
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$FOLDER/$TABLE_NAME.sql"
#Import the data into the tables
echo "Uploading data..."
cat "$FOLDER/$CSV_FILENAME" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.$TABLE_NAME FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo "Done creating $TABLE_NAME table!"
